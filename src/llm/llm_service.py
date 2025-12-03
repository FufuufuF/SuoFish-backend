from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from src.db.models.message import Message
from src.core.config import QWEN_API_KEY, QWEN_URL_BASE, QWEN_MODEL_NAME
from src.schemas.llm_config import LLMConfig

SUMMARY_PROMPT = """请将以下对话历史总结为简洁的摘要，保留关键信息、用户偏好和重要上下文。
摘要应该：
1. 概括对话的主要话题和结论
2. 保留用户明确表达的偏好或要求
3. 记录任何重要的决策或待办事项
4. 控制在300字以内

对话历史：
{conversation}

请直接输出摘要内容，不要有多余的开头或解释。"""


class LLMService:
    def __init__(self, config: LLMConfig = LLMConfig(api_key=QWEN_API_KEY, base_url=QWEN_URL_BASE, model_name=QWEN_MODEL_NAME)):
        self.llm = ChatOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model_name,
        )
        self.agent = create_agent(
            self.llm,
            tools=[]
        )

    async def run(self, messages: List[Message], system_prompt: Optional[str] = None):
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
        for token, metadata in self.agent.stream(
            {'messages': messages_list},
            stream_mode="messages",
        ):  
            yield token, metadata
        
    async def generate_chat_response(self, messages: List[Message], system_prompt: Optional[str] = None):
        async for token, metadata in self.run(messages, system_prompt):
            if metadata.get("langgraph_node") == "model" and token.content:
                yield token.content

    async def generate_summary(self, messages: List[Message]) -> str:
        """生成对话历史的摘要"""
        # 将消息格式化为对话文本
        conversation_text = "\n".join([
            f"{'用户' if msg.role == 'user' else 'AI'}: {msg.content}"
            for msg in messages
        ])
        
        prompt = SUMMARY_PROMPT.format(conversation=conversation_text)
        
        # 使用 LLM 生成摘要（非流式）
        response = await self.llm.ainvoke([{'role': 'user', 'content': prompt}])
        return response.content