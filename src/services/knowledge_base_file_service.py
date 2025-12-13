"""
知识库文件上传服务 - 处理知识库文件的存储和管理
"""
from pathlib import Path
from typing import Optional, List, Tuple

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import knowledge_base_file as kb_file_crud
from src.db.models.knowledge_base_file import KnowledgeBaseFile
from src.utils.file_validator import FileValidator
from src.utils.file_storage import FileStorage


class KnowledgeBaseFileService:
    """知识库文件上传服务"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.validator = FileValidator()
        self.storage = FileStorage()
    
    async def _save_single_file(
        self,
        file: UploadFile,
        knowledge_base_id: int
    ) -> Tuple[Optional[KnowledgeBaseFile], Optional[str]]:
        """
        保存单个上传的文件
        
        Args:
            file: FastAPI 的 UploadFile 对象
            knowledge_base_id: 知识库 ID
            
        Returns:
            (KnowledgeBaseFile 对象, 错误信息) - 成功时错误信息为 None
        """
        # 1. 验证文件（包括读取内容）
        is_valid, error, content = await self.validator.validate_file_full(file)
        if not is_valid:
            return None, error
        
        # 2. 生成存储路径
        storage_path = self.storage.generate_storage_path(
            entity_type="kb",
            entity_id=knowledge_base_id,
            original_filename=file.filename
        )
        
        # 3. 保存文件到磁盘
        success, error = await self.storage.save_file(content, storage_path)
        if not success:
            return None, error
        
        # 4. 创建数据库记录
        file_type = self.validator.get_file_extension(file.filename)
        kb_file = await kb_file_crud.add_file(
            db=self.db,
            knowledge_base_id=knowledge_base_id,
            file_name=file.filename,
            file_type=file_type,
            file_size=len(content),
            file_path=storage_path
        )
        
        return kb_file, None
    
    async def save_files(
        self,
        files: List[UploadFile],
        knowledge_base_id: int
    ) -> Tuple[List[KnowledgeBaseFile], List[str]]:
        """
        批量保存上传的文件
        
        Args:
            files: 文件列表
            knowledge_base_id: 知识库 ID
        
        Returns:
            (成功保存的文件列表, 错误信息列表)
        """
        saved_files = []
        errors = []
        
        for file in files:
            kb_file, error = await self._save_single_file(file, knowledge_base_id)
            if kb_file:
                saved_files.append(kb_file)
            if error:
                errors.append(f"{file.filename}: {error}")
        
        return saved_files, errors
    
    def get_file_path(self, kb_file: KnowledgeBaseFile) -> Optional[Path]:
        """
        获取文件的 Path 对象
        
        Args:
            kb_file: 知识库文件记录
            
        Returns:
            Path 对象，如果文件不存在则返回 None
        """
        path = self.storage.get_file_path(kb_file.file_path)
        if self.storage.file_exists(kb_file.file_path):
            return path
        return None
    
    async def delete_file(self, kb_file: KnowledgeBaseFile) -> bool:
        """
        删除文件（包括物理文件和数据库记录）
        
        Args:
            kb_file: 知识库文件记录
            
        Returns:
            是否删除成功
        """
        try:
            # 删除物理文件
            await self.storage.delete_file(kb_file.file_path)
            
            # 删除数据库记录
            return await kb_file_crud.delete_file(self.db, kb_file.id)
        except Exception:
            return False
    
    async def delete_all_files(self, knowledge_base_id: int) -> bool:
        """
        删除知识库的所有文件（包括物理文件和数据库记录）
        
        Args:
            knowledge_base_id: 知识库 ID
            
        Returns:
            是否删除成功
        """
        try:
            # 获取所有文件
            files = await kb_file_crud.get_files_by_knowledge_base(
                self.db, knowledge_base_id
            )
            
            # 删除物理文件
            for file in files:
                await self.storage.delete_file(file.file_path)
            
            # 删除数据库记录
            return await kb_file_crud.delete_files_by_knowledge_base(
                self.db, knowledge_base_id
            )
        except Exception:
            return False

