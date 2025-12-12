import json
import asyncio
from typing import AsyncGenerator, Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.message import (
    create_messages_batch, 
    get_K_messages_by_conversation_id,
    get_message_count_by_conversation_id,
    get_messages_by_conversation_id,
)
from src.crud.conversation import (
    create_conversation, 
    update_conversation_summary,
    get_conversation_by_id,
)
from src.crud.conversation_file import get_files_by_conversation
from src.db.models.conversation import Conversation
from src.db.models.message import Message
from src.schemas.chat import ChatMetadata
from src.ai.llm import ChatModel
from src.services.file_service import FileService
from src.services.rag_service import get_rag_service, RAGService
from src.api.deps import get_db_context
from src.ai.llm.prompt import build_system_prompt
from src.db.models.model_config import ModelConfig

MAX_CHAT_ROUND = 20  # 保留最近 K 轮对话
SUMMARY_TRIGGER_INTERVAL = 20  # 每 N 条消息触发一次总结
RAG_TOP_K = 5  # RAG 检索返回的最大结果数量


class ChatService:
    """聊天业务逻辑服务"""
    
    def __init__(self, db: AsyncSession, model_config: Optional[ModelConfig] = None):
        self.db = db
        self.chat_model = ChatModel(model_config=model_config)
        self.file_service = FileService(db)
        self.rag_service: RAGService = get_rag_service()
    
    async def trigger_summary_generation(self, conversation_id: int):
        """后台任务：生成对话摘要并保存"""
        async with get_db_context() as db:
            try:
                all_messages = await get_messages_by_conversation_id(db, conversation_id)
                if not all_messages:
                    return
                
                chat_model = ChatModel()
                summary = await chat_model.generate_summary(all_messages)
                
                await update_conversation_summary(db, conversation_id, summary)
            except Exception as e:
                print(f"Failed to generate summary for conversation {conversation_id}: {e}")
    
    async def validate_conversation(self, conversation_id: int, user_id: int) -> tuple[Optional[Conversation], Optional[str]]:
        """
        验证会话是否存在且属于当前用户
        返回: (conversation, error_message)
        """
        if not conversation_id:
            return None, None
        
        conversation = await get_conversation_by_id(self.db, conversation_id)
        if not conversation:
            return None, f"Conversation {conversation_id} not found"
        
        if conversation.user_id != user_id:
            return None, "Unauthorized access to conversation"
        
        return conversation, None
    
    async def get_chat_context(self, conversation_id: Optional[int]) -> list[Message]:
        """获取最近 K 轮对话作为上下文"""
        if not conversation_id:
            return []
        return await get_K_messages_by_conversation_id(self.db, conversation_id, MAX_CHAT_ROUND * 2)
    
    async def generate_llm_response(
        self, 
        messages: list[Message], 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成 LLM 响应"""
        async for token in self.chat_model.generate_chat_response(messages, system_prompt=system_prompt):
            yield token
    
    async def save_messages(
        self, 
        user_message_content: str, 
        llm_message_content: str,
        conversation_id: int
    ) -> tuple[Message, Message]:
        """保存用户消息和 LLM 响应消息"""
        user_message = Message(role='user', content=user_message_content, conversation_id=conversation_id)
        llm_message = Message(role='assistant', content=llm_message_content, conversation_id=conversation_id)
        user_message, llm_message = await create_messages_batch(self.db, [user_message, llm_message])
        return user_message, llm_message
    
    async def create_new_conversation(self, user_id: int, initial_content: str) -> Conversation:
        """创建新会话"""
        name = initial_content[:50] if initial_content else "New Chat"
        conversation = Conversation(user_id=user_id, name=name)
        return await create_conversation(self.db, conversation)
    
    async def should_trigger_summary(self, conversation_id: int) -> bool:
        """检查是否应该触发摘要生成"""
        message_count = await get_message_count_by_conversation_id(self.db, conversation_id)
        return message_count > 0 and message_count % SUMMARY_TRIGGER_INTERVAL == 0
    
    async def process_chat(
        self, 
        user_message: str,
        user_id: int,
        conversation_id: Optional[int] = None,
        files: Optional[list[UploadFile]] = None,
        knowledge_base_ids: Optional[list[int]] = None
    ) -> AsyncGenerator[str, None]:
        """
        处理聊天请求的完整流程
        
        生成格式为 NDJSON:
        - {"token": "..."} - LLM 生成的 token
        - {"error": "..."} - 错误信息
        - {"metadata": {...}} - 完成后的元数据
        - {"save_error": "..."} - 保存时的错误
        - {"files": {...}} - 文件上传结果
        - {"rag_results": {...}} - RAG 检索结果
        """
        llm_response_content = ''
        existing_conversation = None
        summary = None
        
        # 验证会话
        if conversation_id:
            existing_conversation, error = await self.validate_conversation(conversation_id, user_id)
            if error:
                yield f'{{"error": {json.dumps(error)}}}\n'
                return
            summary = existing_conversation.summary
        
        saved_files = []
        rag_context = ""
        
        try:
            # 如果有文件但没有会话，需要先创建会话
            if files and not conversation_id:
                conversation = await self.create_new_conversation(user_id, user_message)
                conversation_id = conversation.id
                existing_conversation = conversation
            
            # 处理文件上传
            if files and conversation_id:
                saved_files, file_errors = await self.file_service.save_files(
                    files=files,
                    conversation_id=conversation_id,
                    user_id=user_id
                )
                
                # 返回文件处理结果
                files_result = {
                    "saved": [
                        {"id": f.id, "name": f.file_name, "type": f.file_type, "size": f.file_size}
                        for f in saved_files
                    ],
                    "errors": file_errors
                }
                yield f'{{"files": {json.dumps(files_result)}}}\n'
                
                # 对上传的文件进行嵌入处理
                for saved_file in saved_files:
                    try:
                        file_path = self.file_service.get_file_path(saved_file)
                        self.rag_service.embed_conversation_file(
                            file_path=file_path,
                            file_id=saved_file.id,
                            conversation_id=conversation_id,
                            user_id=user_id,
                            file_name=saved_file.file_name  # 传递文件名用于 RAG 上下文展示
                        )
                    except Exception as embed_error:
                        # 嵌入失败不阻塞聊天流程，只记录错误
                        print(f"Failed to embed file {saved_file.file_name}: {embed_error}")
            
            # 获取会话中的文件列表（用于系统提示词）
            file_names = []
            if conversation_id:
                conversation_files = await get_files_by_conversation(self.db, conversation_id)
                file_names = [f.file_name for f in conversation_files]
            
            # RAG 检索（如果有会话 ID）
            if conversation_id:
                rag_results = self.rag_service.retrieve_with_knowledge_base(
                    query=user_message,
                    conversation_id=conversation_id,
                    knowledge_base_ids=knowledge_base_ids,
                    top_k=RAG_TOP_K
                )
                
                if rag_results:
                    # 返回 RAG 检索结果给前端
                    rag_results_data = {
                        "count": len(rag_results),
                        "results": [
                            {
                                "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                                "score": round(r.score, 4),
                                "source_type": r.metadata.get("source_type", "unknown"),
                                "file_id": r.metadata.get("file_id"),
                                "file_name": r.metadata.get("file_name"),
                                "knowledge_base_id": r.metadata.get("knowledge_base_id"),
                                "page": r.metadata.get("page"),
                            }
                            for r in rag_results
                        ]
                    }
                    yield f'{{"rag_results": {json.dumps(rag_results_data, ensure_ascii=False)}}}\n'
                    
                    # 格式化为 LLM 上下文
                    rag_context = self.rag_service.format_context(rag_results)
            
            # 构建系统提示词（包含摘要、RAG 上下文和文件列表）
            system_prompt = self._build_system_prompt(summary, rag_context, file_names)
            
            # 构建消息上下文
            messages = await self.get_chat_context(conversation_id)
            messages.append(Message(role='user', content=user_message, conversation_id=conversation_id))
            
            # 流式生成响应
            async for token in self.generate_llm_response(messages, system_prompt=system_prompt):
                llm_response_content += token
                yield f'{{"token": {json.dumps(token)}}}\n'
        except Exception as e:
            yield f'{{"error": {json.dumps(str(e))}}}\n'
        finally:
            try:
                # 确定会话（如果还没创建）
                if not conversation_id:
                    conversation = await self.create_new_conversation(user_id, llm_response_content)
                    conversation_id = conversation.id
                else:
                    conversation = existing_conversation
                
                # 保存消息
                user_msg, llm_msg = await self.save_messages(user_message, llm_response_content, conversation_id)
                
                # 检查是否需要触发摘要
                if await self.should_trigger_summary(conversation_id):
                    asyncio.create_task(self.trigger_summary_generation(conversation_id))
                
                # 返回元数据
                metadata = ChatMetadata(
                    llm_message_id=llm_msg.id,
                    user_message_id=user_msg.id,
                    conversation_id=conversation_id,
                    conversation_name=conversation.name,
                    created_at=int(conversation.created_at.timestamp() * 1000),
                    updated_at=int(conversation.updated_at.timestamp() * 1000),
                )
                yield f'{{"metadata": {metadata.model_dump_json()}}}\n'
            except Exception as save_error:
                yield f'{{"save_error": {json.dumps(str(save_error))}}}\n'
    
    def _build_system_prompt(
        self, 
        summary: Optional[str], 
        rag_context: Optional[str],
        file_names: Optional[list[str]] = None
    ) -> Optional[str]:
        """
        构建系统提示词
        
        Args:
            summary: 对话摘要
            rag_context: RAG 检索到的上下文
            file_names: 用户上传的文件名列表
        """
        return build_system_prompt(
            summary=summary,
            rag_context=rag_context,
            file_names=file_names
        )
