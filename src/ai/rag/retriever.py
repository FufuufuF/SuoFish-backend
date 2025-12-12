"""
检索器 - 从向量存储中检索相关文档
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from src.ai.rag.embedding import Embedding
from src.ai.rag.vector_store import ChromaVectorStore, get_vector_store


@dataclass
class RetrievalResult:
    """检索结果"""
    content: str
    score: float
    metadata: dict


class BaseRetriever(ABC):
    """检索器抽象基类"""
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """根据查询检索相关文档"""
        pass


class DocumentRetriever(BaseRetriever):
    """基于向量相似度的文档检索器"""
    
    def __init__(
        self, 
        embedding: Optional[Embedding] = None,
        vector_store: Optional[ChromaVectorStore] = None
    ):
        self._embedding = embedding or Embedding()
        self._vector_store = vector_store or get_vector_store()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        检索与查询最相关的文档
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数量
            
        Returns:
            检索结果列表，按相关性排序
        """
        # 1. 将查询向量化
        query_vector = self._embedding.embed_text(query)
        
        # 2. 在向量存储中搜索
        results = self._vector_store.search(query_vector, top_k=top_k)
        
        # 3. 转换为 RetrievalResult 格式
        return [
            RetrievalResult(
                content=doc,
                score=1 - distance if distance is not None else 0,  # 余弦距离转相似度
                metadata=metadata or {}
            )
            for doc, distance, metadata in results
        ]
    
    def retrieve_by_file_id(
        self, 
        query: str, 
        file_id: int, 
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        在指定文件范围内检索
        
        Args:
            query: 查询文本
            file_id: 文件 ID
            top_k: 返回的最大结果数量
        """
        query_vector = self._embedding.embed_text(query)
        results = self._vector_store.search_by_file_id(query_vector, file_id, top_k=top_k)
        
        return [
            RetrievalResult(
                content=doc,
                score=1 - distance if distance is not None else 0,
                metadata=metadata or {}
            )
            for doc, distance, metadata in results
        ]
    
    def retrieve_by_file_ids(
        self, 
        query: str, 
        file_ids: List[int], 
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        在多个文件范围内检索
        
        Args:
            query: 查询文本
            file_ids: 文件 ID 列表
            top_k: 返回的最大结果数量
        """
        query_vector = self._embedding.embed_text(query)
        results = self._vector_store.search_by_file_ids(query_vector, file_ids, top_k=top_k)
        
        return [
            RetrievalResult(
                content=doc,
                score=1 - distance if distance is not None else 0,
                metadata=metadata or {}
            )
            for doc, distance, metadata in results
        ]
    
    def retrieve_by_conversation(
        self,
        query: str,
        conversation_id: int,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        在指定会话范围内检索（只检索会话文件）
        
        Args:
            query: 查询文本
            conversation_id: 会话 ID
            top_k: 返回的最大结果数量
        """
        query_vector = self._embedding.embed_text(query)
        results = self._vector_store.search_with_filter(
            query_vector, 
            where={"conversation_id": conversation_id},
            top_k=top_k
        )
        
        return [
            RetrievalResult(
                content=doc,
                score=1 - distance if distance is not None else 0,
                metadata=metadata or {}
            )
            for doc, distance, metadata in results
        ]
    
    def retrieve_with_knowledge_base(
        self,
        query: str,
        conversation_id: int,
        knowledge_base_ids: Optional[List[int]] = None,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        同时检索会话文件和知识库
        
        Args:
            query: 查询文本
            conversation_id: 会话 ID
            knowledge_base_ids: 知识库 ID 列表，None 表示不检索知识库
            top_k: 返回的最大结果数量
        """
        query_vector = self._embedding.embed_text(query)
        
        # 构建查询条件
        if knowledge_base_ids:
            # 检索会话文件 + 指定知识库
            where = {
                "$or": [
                    {"conversation_id": conversation_id},
                    {
                        "$and": [
                            {"source_type": "knowledge_base"},
                            {"knowledge_base_id": {"$in": knowledge_base_ids}}
                        ]
                    }
                ]
            }
        else:
            # 只检索会话文件
            where = {"conversation_id": conversation_id}
        
        results = self._vector_store.search_with_filter(query_vector, where=where, top_k=top_k)
        
        return [
            RetrievalResult(
                content=doc,
                score=1 - distance if distance is not None else 0,
                metadata=metadata or {}
            )
            for doc, distance, metadata in results
        ]
    
    def format_context(self, results: List[RetrievalResult], separator: str = "\n\n---\n\n") -> str:
        """
        将检索结果格式化为上下文字符串，供 LLM 使用
        
        注意：推荐使用 src.ai.llm.prompt.rag.format_rag_context 函数，
        该方法保留用于向后兼容。
        
        Args:
            results: 检索结果列表
            separator: 分隔符
            
        Returns:
            格式化后的上下文字符串
        """
        from src.ai.llm.prompt.rag import format_rag_context
        return format_rag_context(results, separator)


# 便捷函数
def get_retriever(
    embedding: Optional[Embedding] = None,
    vector_store: Optional[ChromaVectorStore] = None
) -> DocumentRetriever:
    """获取检索器实例"""
    return DocumentRetriever(embedding, vector_store)
