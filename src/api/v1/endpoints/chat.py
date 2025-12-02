import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.curd.message import create_messages_batch
from src.curd.conversation import create_conversation
from src.db.models.conversation import Conversation
from src.db.models.message import Message
from src.shcemas.llm_config import ChatMetadata
from src.llm.llm_service import LLMService
from src.shcemas.chat import Chat
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
async def chat(
    chat: Chat,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    async def generate():
        llm_service = LLMService()
        llm_message = Message(role='assistant', content='')
        conversation_id = chat.conversation_id if chat.conversation_id else None
        
        # 验证会话是否存在
        if conversation_id:
            from src.curd.conversation import get_conversation_by_id
            existing_conversation = get_conversation_by_id(db, conversation_id)
            if not existing_conversation:
                yield f'{{"error": {json.dumps(f"Conversation {conversation_id} not found")}}}\n'
                return
            # 验证会话是否属于当前用户
            if existing_conversation.user_id != user_id:
                yield f'{{"error": {json.dumps("Unauthorized access to conversation")}}}\n'
                return
        
        try:
            # 流式生成响应
            async for token in llm_service.generate_chat_response(chat.user_message):
                llm_message.content += token
                # 使用 json.dumps 正确转义特殊字符
                yield f'{{"token": {json.dumps(token)}}}\n'
        except Exception as e:
            # LLM异常时也要保存已生成的内容
            yield f'{{"error": {json.dumps(str(e))}}}\n'
        finally:
            # 确保无论如何都保存数据（即使客户端断开或发生异常）
            try:
                if not conversation_id:
                    conversation = Conversation(user_id=user_id, name=llm_message.content[:50] if llm_message.content else "New Chat")
                    conversation = create_conversation(db, conversation)
                    conversation_id = conversation.id

                # 用户消息
                user_message = Message(role='user', content=chat.user_message, conversation_id=conversation_id)
                # LLM消息（即使为空也保存）
                llm_message.conversation_id = conversation_id

                user_message, llm_message = create_messages_batch(db, [user_message, llm_message])
                
                metadata_json = ChatMetadata(
                    llm_message_id=llm_message.id,
                    user_message_id=user_message.id,
                    conversation_id=conversation_id,
                    conversation_name=conversation.name,
                    created_at=int(conversation.created_at.timestamp() * 1000),
                    updated_at=int(conversation.updated_at.timestamp() * 1000),
                )
                yield f'{{"metadata": {metadata_json.model_dump_json()}}}\n'
            except Exception as save_error:
                # 保存失败也要记录，但不影响流式响应
                yield f'{{"save_error": {json.dumps(str(save_error))}}}\n'
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")