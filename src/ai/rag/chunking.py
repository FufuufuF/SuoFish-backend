"""
文档分块器 - 将长文档切分为适合向量化的片段
"""
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader


class FileChunker():
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )

    def _load_document(self, doc_path: Path) -> List[Document]:
        """根据文件类型加载文档"""
        file_suffix = doc_path.suffix.lower()
        if file_suffix == '.pdf':
            loader = PyPDFLoader(str(doc_path))
        elif file_suffix == '.docx':
            loader = Docx2txtLoader(str(doc_path))
        elif file_suffix == '.pptx':
            loader = UnstructuredPowerPointLoader(str(doc_path))
        else:
            raise ValueError(f'不支持的文件类型: {file_suffix}')
        return loader.load()

    def split_conversation_file(
        self, 
        doc_path: Path, 
        file_id: int,
        conversation_id: int,
        user_id: int,
        file_name: Optional[str] = None
    ) -> List[Document]:
        """
        分块会话文件
        
        Args:
            doc_path: 文件路径
            file_id: 文件 ID (对应 MySQL conversation_file.id)
            conversation_id: 会话 ID
            user_id: 用户 ID
            file_name: 文件名（用于在 RAG 检索结果中显示来源）
        """
        docs = self._load_document(doc_path)
        chunked_documents = self.text_splitter.split_documents(docs)
        
        # 使用传入的文件名，如果没有则使用路径中的文件名
        actual_file_name = file_name or doc_path.name
        
        for i, chunk in enumerate(chunked_documents):
            chunk.metadata.update({
                "source_type": "conversation_file",
                "file_id": file_id,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "chunk_index": i,
                "file_name": actual_file_name,
            })
        
        return chunked_documents

    def split_knowledge_base_file(
        self, 
        doc_path: Path,
        file_id: int,
        knowledge_base_id: int,
        user_id: int,
        file_name: Optional[str] = None
    ) -> List[Document]:
        """
        分块知识库文件
        
        Args:
            doc_path: 文件路径
            file_id: 文件 ID (对应 MySQL knowledge_base_file.id)
            knowledge_base_id: 知识库 ID
            user_id: 用户 ID
            file_name: 文件名（可选，用于溯源）
        """
        docs = self._load_document(doc_path)
        chunked_documents = self.text_splitter.split_documents(docs)
        
        for i, chunk in enumerate(chunked_documents):
            chunk.metadata.update({
                "source_type": "knowledge_base",
                "file_id": file_id,
                "knowledge_base_id": knowledge_base_id,
                "user_id": user_id,
                "chunk_index": i,
                "file_name": file_name or doc_path.name,
            })
        
        return chunked_documents


if __name__ == '__main__':
    chunker = FileChunker()
    
    # 测试会话文件分块
    chunks = chunker.split_conversation_file(
        doc_path=Path('/Users/haoxuan.huang/Desktop/szu/ChatBot/backend/定性研究-要求.docx'),
        file_id=1,
        conversation_id=5,
        user_id=1
    )
    
    print(f'分块后的文档数量: {len(chunks)}')
    for chunk in chunks:
        print("==============元数据===============")
        print(chunk.metadata)
        print("==============内容===============")
        print(chunk.page_content[:100] + "...")