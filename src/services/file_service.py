"""
文件上传服务 - 处理文件的存储和管理
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.crud import conversation_file as file_crud
from src.db.models.conversation_file import ConversationFile


# 允许的文件类型
ALLOWED_EXTENSIONS = {"docx", "pptx", "xlsx", "json", "md", "txt"}

# 文件大小限制（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024

# 文件存储根目录
UPLOAD_DIR = Path("uploads")


class FileService:
    """文件上传服务"""
    
    def __init__(self, db: Session):
        self.db = db
        # 确保上传目录存在
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名（不含点号）"""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    def _validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """
        验证文件是否合法
        返回: (是否合法, 错误信息)
        """
        # 检查文件名
        if not file.filename:
            return False, "文件名不能为空"
        
        # 检查文件类型
        ext = self._get_file_extension(file.filename)
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"不支持的文件类型: {ext}，允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        
        return True, ""
    
    def _generate_storage_path(self, conversation_id: int, original_filename: str) -> str:
        """
        生成存储路径
        格式: uploads/{conversation_id}/{date}/{uuid}_{original_filename}
        """
        date_str = datetime.utcnow().strftime("%Y/%m/%d")
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = original_filename.replace(" ", "_")
        
        return str(UPLOAD_DIR / str(conversation_id) / date_str / f"{unique_id}_{safe_filename}")
    
    async def save_file(
        self,
        file: UploadFile,
        conversation_id: int,
        user_id: int
    ) -> tuple[Optional[ConversationFile], Optional[str]]:
        """
        保存上传的文件
        
        Args:
            file: FastAPI 的 UploadFile 对象
            conversation_id: 会话 ID
            user_id: 用户 ID
            
        Returns:
            (ConversationFile 对象, 错误信息) - 成功时错误信息为 None
        """
        # 验证文件
        is_valid, error_msg = self._validate_file(file)
        if not is_valid:
            return None, error_msg
        
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 检查文件大小
        if file_size > MAX_FILE_SIZE:
            return None, f"文件过大，最大允许 {MAX_FILE_SIZE // 1024 // 1024}MB"
        
        if file_size == 0:
            return None, "文件内容为空"
        
        # 生成存储路径
        storage_path = self._generate_storage_path(conversation_id, file.filename)
        
        # 确保目录存在
        Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        try:
            with open(storage_path, "wb") as f:
                f.write(content)
        except Exception as e:
            return None, f"文件保存失败: {str(e)}"
        
        # 创建数据库记录
        file_type = self._get_file_extension(file.filename)
        conversation_file = file_crud.add_file(
            db=self.db,
            conversation_id=conversation_id,
            user_id=user_id,
            file_name=file.filename,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path
        )
        
        return conversation_file, None
    
    async def save_files(
        self,
        files: list[UploadFile],
        conversation_id: int,
        user_id: int
    ) -> tuple[list[ConversationFile], list[str]]:
        """
        批量保存上传的文件
        
        Returns:
            (成功保存的文件列表, 错误信息列表)
        """
        saved_files = []
        errors = []
        
        for file in files:
            conversation_file, error = await self.save_file(file, conversation_id, user_id)
            if conversation_file:
                saved_files.append(conversation_file)
            if error:
                errors.append(f"{file.filename}: {error}")
        
        return saved_files, errors
    
    def get_file_content(self, conversation_file: ConversationFile) -> Optional[bytes]:
        """读取文件内容"""
        try:
            with open(conversation_file.storage_path, "rb") as f:
                return f.read()
        except Exception:
            return None
    
    def delete_file(self, conversation_file: ConversationFile) -> bool:
        """删除文件（包括物理文件和数据库记录）"""
        try:
            # 删除物理文件
            if os.path.exists(conversation_file.storage_path):
                os.remove(conversation_file.storage_path)
            
            # 删除数据库记录
            return file_crud.delete_file(self.db, conversation_file.id)
        except Exception:
            return False

