"""
向量存储 - 存储和管理文档向量（预留）
"""
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseVectorStore(ABC):
    """向量存储抽象基类"""
    
    @abstractmethod
    async def add_vectors(
        self, 
        vectors: List[List[float]], 
        documents: List[str],
        metadatas: Optional[List[dict]] = None
    ) -> List[str]:
        """添加向量到存储，返回 ID 列表"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5
    ) -> List[tuple]:
        """搜索最相似的向量，返回 (document, score, metadata) 列表"""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """删除指定 ID 的向量"""
        pass

