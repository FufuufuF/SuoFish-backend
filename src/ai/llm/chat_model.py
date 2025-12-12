from typing import AsyncGenerator, List, Optional

from langchain_openai import ChatOpenAI

from src.core.config import llm as llm_config
from src.db.models.model_config import ModelConfig
from src.db.models.message import Message
from src.ai.llm.prompt import SUMMARY_PROMPT, SYSTEM_PROMPT_BASE
from .base import BaseLLM


class ChatModel(BaseLLM):
    """聊天模型实现"""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        if model_config:
            self.client = ChatOpenAI(
                api_key=model_config.api_key,
                base_url=model_config.base_url,
                model=model_config.model_name,
            )
        else:
            self.client = ChatOpenAI(
                api_key=llm_config.api_key,
                base_url=llm_config.base_url,
                model=llm_config.model_name,
            )
        self.system_prompt = SYSTEM_PROMPT_BASE
    
    async def generate(self, messages: List[dict]) -> str:
        """非流式生成"""
        response = await self.client.ainvoke(messages)
        return response.content
    
    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        """流式生成"""
        async for chunk in self.client.astream(messages):
            if chunk.content:
                yield chunk.content
    
    async def run(self, messages: List[Message], system_prompt: Optional[str] = None):
        """
        运行聊天模型
        
        Args:
            messages: 消息列表（Message 模型）
            system_prompt: 可选的系统提示（如对话摘要）
        """
        messages_list = []
        
        # 始终添加基础系统提示词
        messages_list.append({
            'role': 'system',
            'content': self.system_prompt
        })
        
        # 如果有摘要，追加摘要
        if system_prompt:
            messages_list.append({
                'role': 'system',
                'content': f"以下是之前对话的摘要，请参考：\n{system_prompt}"
            })
        
        messages_list.extend([
            {'role': message.role, 'content': message.content} for message in messages
        ])
        
        async for chunk in self.client.astream(messages_list):
            yield chunk
    
    async def generate_chat_response(self, messages: List[Message], system_prompt: Optional[str] = None):
        """流式生成聊天响应"""
        async for chunk in self.run(messages, system_prompt):
            if chunk.content:
                yield chunk.content

    async def generate_summary(self, messages: List[Message]) -> str:
        """生成对话历史的摘要"""
        # 将消息格式化为对话文本
        conversation_text = "\n".join([
            f"{'用户' if msg.role == 'user' else 'AI'}: {msg.content}"
            for msg in messages
        ])
        
        prompt = SUMMARY_PROMPT.format(conversation=conversation_text)
        
        # 使用 LLM 生成摘要（非流式）
        response = await self.client.ainvoke([{'role': 'user', 'content': prompt}])
        return response.content

