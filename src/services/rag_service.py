"""
RAG 服务 - 提供文件嵌入和检索的统一接口
"""
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from src.ai.rag.chunking import FileChunker
from src.ai.rag.embedding import Embedding
from src.ai.rag.vector_store import get_vector_store
from src.ai.rag.retriever import RetrievalResult, get_retriever


@dataclass
class EmbedResult:
    """嵌入结果"""
    file_id: int
    chunk_count: int
    vector_ids: List[str]


class RAGService:
    """RAG 服务：负责文件嵌入和检索"""

    def __init__(self):
        self._chunker = FileChunker()
        self._embedding = Embedding()
        self._vector_store = get_vector_store()
        self._retriever = get_retriever(self._embedding, self._vector_store)

    # ==================== 嵌入相关 ====================

    def embed_conversation_file(
        self,
        file_path: Path,
        file_id: int,
        conversation_id: int,
        user_id: int,
        file_name: Optional[str] = None
    ) -> EmbedResult:
        """
        嵌入会话文件
        
        Args:
            file_path: 文件路径
            file_id: 文件 ID (MySQL conversation_file.id)
            conversation_id: 会话 ID
            user_id: 用户 ID
            file_name: 文件名（用于在 RAG 检索结果中显示来源）
            
        Returns:
            嵌入结果，包含分块数量和向量 ID 列表
        """
        # 1. 分块
        chunks = self._chunker.split_conversation_file(
            doc_path=file_path,
            file_id=file_id,
            conversation_id=conversation_id,
            user_id=user_id,
            file_name=file_name
        )
        
        # 2. 向量化
        texts = [chunk.page_content for chunk in chunks]
        vectors = self._embedding.embed_texts(texts)
        metadatas = [chunk.metadata for chunk in chunks]
        
        # 3. 存入向量存储
        vector_ids = self._vector_store.add_vectors(vectors, texts, metadatas)
        
        return EmbedResult(
            file_id=file_id,
            chunk_count=len(chunks),
            vector_ids=vector_ids
        )

    def embed_knowledge_base_file(
        self,
        file_path: Path,
        knowledge_base_id: int,
        user_id: int,
        file_name: Optional[str] = None
    ) -> EmbedResult:
        """
        嵌入知识库文件
        
        Args:
            file_path: 文件路径
            knowledge_base_id: 知识库 ID
            user_id: 用户 ID
            file_name: 文件名（可选）
            
        Returns:
            嵌入结果
        """
        # 1. 分块
        chunks = self._chunker.split_knowledge_base_file(
            doc_path=file_path,
            knowledge_base_id=knowledge_base_id,
            user_id=user_id,
            file_name=file_name
        )
        
        # 2. 向量化
        texts = [chunk.page_content for chunk in chunks]
        vectors = self._embedding.embed_texts(texts)
        metadatas = [chunk.metadata for chunk in chunks]
        
        # 3. 存入向量存储
        vector_ids = self._vector_store.add_vectors(vectors, texts, metadatas)
        
        return EmbedResult(
            file_id=knowledge_base_id,
            chunk_count=len(chunks),
            vector_ids=vector_ids
        )

    # ==================== 检索相关 ====================

    def retrieve_by_conversation(
        self,
        query: str,
        conversation_id: int,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        在指定会话范围内检索
        
        Args:
            query: 查询文本
            conversation_id: 会话 ID
            top_k: 返回的最大结果数量
        """
        return self._retriever.retrieve_by_conversation(query, conversation_id, top_k)

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
        return self._retriever.retrieve_with_knowledge_base(
            query, conversation_id, knowledge_base_ids, top_k
        )

    def format_context(
        self,
        results: List[RetrievalResult],
        separator: str = "\n\n---\n\n"
    ) -> str:
        """
        将检索结果格式化为上下文字符串，供 LLM 使用
        
        Args:
            results: 检索结果列表
            separator: 分隔符
        """
        from src.ai.llm.prompt.rag import format_rag_context
        return format_rag_context(results, separator)

    # ==================== 删除相关 ====================

    def delete_file_vectors(self, file_id: int) -> bool:
        """
        删除指定文件的所有向量
        
        Args:
            file_id: 文件 ID
        """
        return self._vector_store.delete_by_file_id(file_id)

    def delete_conversation_vectors(self, conversation_id: int) -> bool:
        """
        删除指定会话的所有向量
        
        Args:
            conversation_id: 会话 ID
        """
        return self._vector_store.delete_by_metadata({"conversation_id": conversation_id})

    def delete_knowledge_base_vectors(self, knowledge_base_id: int) -> bool:
        """
        删除指定知识库的所有向量
        
        Args:
            knowledge_base_id: 知识库 ID
        """
        return self._vector_store.delete_by_metadata({"knowledge_base_id": knowledge_base_id})

    # ==================== 统计相关 ====================

    def get_total_vector_count(self) -> int:
        """获取向量总数"""
        return self._vector_store.count()


# 便捷函数：获取 RAG 服务单例
_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """获取 RAG 服务实例（单例）"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
