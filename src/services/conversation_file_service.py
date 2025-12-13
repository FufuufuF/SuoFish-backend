"""
会话文件上传服务 - 处理会话文件的存储和管理
"""
from pathlib import Path
from typing import Optional, List, Tuple

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import conversation_file as file_crud
from src.db.models.conversation_file import ConversationFile
from src.utils.file_validator import FileValidator
from src.utils.file_storage import FileStorage


class ConversationFileService:
    """会话文件上传服务"""
    
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
        conversation_id: int,
        user_id: int
    ) -> Tuple[Optional[ConversationFile], Optional[str]]:
        """
        保存单个上传的文件
        
        Args:
            file: FastAPI 的 UploadFile 对象
            conversation_id: 会话 ID
            user_id: 用户 ID
            
        Returns:
            (ConversationFile 对象, 错误信息) - 成功时错误信息为 None
        """
        # 1. 验证文件（包括读取内容）
        is_valid, error, content = await self.validator.validate_file_full(file)
        if not is_valid:
            return None, error
        
        # 2. 生成存储路径
        storage_path = self.storage.generate_storage_path(
            entity_type="conversation",
            entity_id=conversation_id,
            original_filename=file.filename
        )
        
        # 3. 保存文件到磁盘
        success, error = await self.storage.save_file(content, storage_path)
        if not success:
            return None, error
        
        # 4. 创建数据库记录
        file_type = self.validator.get_file_extension(file.filename)
        conversation_file = await file_crud.add_file(
            db=self.db,
            conversation_id=conversation_id,
            user_id=user_id,
            file_name=file.filename,
            file_type=file_type,
            file_size=len(content),
            storage_path=storage_path
        )
        
        return conversation_file, None
    
    async def save_files(
        self,
        files: List[UploadFile],
        conversation_id: int,
        user_id: int
    ) -> Tuple[List[ConversationFile], List[str]]:
        """
        批量保存上传的文件
        
        Args:
            files: 文件列表
            conversation_id: 会话 ID
            user_id: 用户 ID
        
        Returns:
            (成功保存的文件列表, 错误信息列表)
        """
        saved_files = []
        errors = []
        
        for file in files:
            conversation_file, error = await self._save_single_file(
                file, conversation_id, user_id
            )
            if conversation_file:
                saved_files.append(conversation_file)
            if error:
                errors.append(f"{file.filename}: {error}")
        
        return saved_files, errors
    
    def get_file_path(self, conversation_file: ConversationFile) -> Optional[Path]:
        """
        获取文件的 Path 对象
        
        Args:
            conversation_file: 会话文件记录
            
        Returns:
            Path 对象，如果文件不存在则返回 None
        """
        path = self.storage.get_file_path(conversation_file.storage_path)
        if self.storage.file_exists(conversation_file.storage_path):
            return path
        return None
    
    async def delete_file(self, conversation_file: ConversationFile) -> bool:
        """
        删除文件（包括物理文件和数据库记录）
        
        Args:
            conversation_file: 会话文件记录
            
        Returns:
            是否删除成功
        """
        try:
            # 删除物理文件
            await self.storage.delete_file(conversation_file.storage_path)
            
            # 删除数据库记录
            return await file_crud.delete_file(self.db, conversation_file.id)
        except Exception:
            return False

