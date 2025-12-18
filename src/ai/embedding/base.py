from abc import ABC, abstractmethod
from typing import List


class BaseEmbedding(ABC):
    """Embedding 抽象基类（预留）"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """将单个文本转换为向量"""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        pass





