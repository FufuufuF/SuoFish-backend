"""
文档分块器 - 将长文档切分为适合向量化的片段（预留）
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class Chunk:
    """文档分块"""
    content: str
    metadata: dict  # 来源文件、页码等


class BaseChunker(ABC):
    """分块器抽象基类"""
    
    @abstractmethod
    def split(self, text: str, metadata: dict = None) -> List[Chunk]:
        """将文本分割为多个片段"""
        pass


class RecursiveChunker(BaseChunker):
    """递归分块器（预留实现）"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str, metadata: dict = None) -> List[Chunk]:
        """TODO: 实现递归分块逻辑"""
        # 预留实现
        if metadata is None:
            metadata = {}
        return [Chunk(content=text, metadata=metadata)]

