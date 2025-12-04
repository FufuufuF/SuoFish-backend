from typing import AsyncGenerator, List, Optional

from langchain_openai import ChatOpenAI

from src.core.config import llm as llm_config
from src.db.models.message import Message
from .base import BaseLLM


SUMMARY_PROMPT = """请将以下对话历史总结为简洁的摘要，保留关键信息、用户偏好和重要上下文。
摘要应该：
1. 概括对话的主要话题和结论
2. 保留用户明确表达的偏好或要求
3. 记录任何重要的决策或待办事项
4. 控制在300字以内

对话历史：
{conversation}

请直接输出摘要内容，不要有多余的开头或解释。"""


class ChatModel(BaseLLM):
    """聊天模型实现"""
    
    def __init__(self):
        self.client = ChatOpenAI(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            model=llm_config.model_name,
        )
    
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
        # 如果有 system prompt (summary)，添加到消息列表开头
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

