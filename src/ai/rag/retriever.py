"""
检索器 - 从向量存储中检索相关文档（预留）
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class RetrievalResult:
    """检索结果"""
    content: str
    score: float
    metadata: dict


class BaseRetriever(ABC):
    """检索器抽象基类"""
    
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """根据查询检索相关文档"""
        pass

