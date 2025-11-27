from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from src.core.config import QWEN_API_KEY, QWEN_URL_BASE, QWEN_MODEL_NAME
from src.shcemas.llm_config import LLMConfig

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

    async def run(self, message: str):
        for token, metadata in self.agent.stream(
            {'messages': [{'role': 'user', 'content': message}]},
            stream_mode="messages",
        ):  
            yield token, metadata
        
    async def generate_chat_response(self, message: str):
        async for token, metadata in self.run(message):
            if metadata.get("langgraph_node") == "model" and token.content:
                yield token.content