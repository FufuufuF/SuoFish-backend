"""
向量存储 - 存储和管理文档向量
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

import chromadb
from chromadb.config import Settings

from src.core.config.database import chroma_settings


class BaseVectorStore(ABC):
    """向量存储抽象基类"""
    
    @abstractmethod
    def add_vectors(
        self, 
        vectors: List[List[float]], 
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加向量到存储，返回 ID 列表"""
        pass
    
    @abstractmethod
    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5
    ) -> List[tuple]:
        """搜索最相似的向量，返回 (document, score, metadata) 列表"""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        """删除指定 ID 的向量"""
        pass


class ChromaVectorStore(BaseVectorStore):
    """基于 Chroma 的向量存储实现"""
    
    _instance: Optional["ChromaVectorStore"] = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式：确保整个应用只有一个 Chroma 客户端实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, collection_name: Optional[str] = None):
        # 避免重复初始化
        if hasattr(self, "_initialized") and self._initialized:
            return
            
        self._client = chromadb.PersistentClient(
            path=chroma_settings.path,
            settings=Settings(anonymized_telemetry=False)
        )
        self._collection_name = collection_name or chroma_settings.collection_name
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        self._initialized = True
    
    @property
    def collection(self):
        """获取当前集合"""
        return self._collection
    
    def get_or_create_collection(self, name: str):
        """获取或创建指定名称的集合"""
        return self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_vectors(
        self, 
        vectors: List[List[float]], 
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加向量到存储"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        self._collection.add(
            embeddings=vectors,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5
    ) -> List[tuple]:
        """搜索最相似的向量"""
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # 整理返回格式: (document, distance, metadata)
        output = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                doc = results["documents"][0][i]
                distance = results["distances"][0][i] if results["distances"] else None
                metadata = results["metadatas"][0][i] if results["metadatas"] else None
                output.append((doc, distance, metadata))
        
        return output
    
    def delete(self, ids: List[str]) -> bool:
        """删除指定 ID 的向量"""
        try:
            self._collection.delete(ids=ids)
            return True
        except Exception:
            return False
    
    def delete_by_metadata(self, where: dict) -> bool:
        """根据元数据条件删除向量"""
        try:
            self._collection.delete(where=where)
            return True
        except Exception:
            return False
    
    def delete_by_file_id(self, file_id: int) -> bool:
        """删除指定文件的所有向量"""
        return self.delete_by_metadata({"file_id": file_id})
    
    def search_by_file_id(
        self, 
        query_vector: List[float], 
        file_id: int,
        top_k: int = 5
    ) -> List[tuple]:
        """在指定文件范围内搜索最相似的向量"""
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where={"file_id": file_id},  # 只在该文件的chunks中搜索
            include=["documents", "metadatas", "distances"]
        )
        
        output = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                doc = results["documents"][0][i]
                distance = results["distances"][0][i] if results["distances"] else None
                metadata = results["metadatas"][0][i] if results["metadatas"] else None
                output.append((doc, distance, metadata))
        
        return output
    
    def search_by_file_ids(
        self, 
        query_vector: List[float], 
        file_ids: List[int],
        top_k: int = 5
    ) -> List[tuple]:
        """在多个文件范围内搜索最相似的向量"""
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where={"file_id": {"$in": file_ids}},  # 在这些文件中搜索
            include=["documents", "metadatas", "distances"]
        )
        
        output = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                doc = results["documents"][0][i]
                distance = results["distances"][0][i] if results["distances"] else None
                metadata = results["metadatas"][0][i] if results["metadatas"] else None
                output.append((doc, distance, metadata))
        
        return output
    
    def search_with_filter(
        self,
        query_vector: List[float],
        where: dict,
        top_k: int = 5
    ) -> List[tuple]:
        """使用自定义过滤条件搜索向量"""
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        output = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                doc = results["documents"][0][i]
                distance = results["distances"][0][i] if results["distances"] else None
                metadata = results["metadatas"][0][i] if results["metadatas"] else None
                output.append((doc, distance, metadata))
        
        return output
    
    def get_by_file_id(self, file_id: int) -> dict:
        """获取指定文件的所有向量数据"""
        return self._collection.get(
            where={"file_id": file_id},
            include=["documents", "metadatas", "embeddings"]
        )
    
    def count(self) -> int:
        """返回集合中的向量数量"""
        return self._collection.count()


# 创建全局单例实例（懒加载方式使用）
def get_vector_store(collection_name: Optional[str] = None) -> ChromaVectorStore:
    """获取向量存储实例"""
    return ChromaVectorStore(collection_name)
