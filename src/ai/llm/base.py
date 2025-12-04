from abc import ABC, abstractmethod
from typing import AsyncGenerator, List


class BaseLLM(ABC):
    """LLM 抽象基类，便于未来切换模型"""
    
    @abstractmethod
    async def generate(self, messages: List[dict]) -> str:
        """非流式生成"""
        pass
    
    @abstractmethod
    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        """流式生成"""
        pass

