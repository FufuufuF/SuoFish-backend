"""
文件验证工具 - 提供文件类型、大小等验证功能
"""
from typing import Tuple, Set
from fastapi import UploadFile


# 允许的文件类型
ALLOWED_EXTENSIONS = {"docx", "pptx", "pdf", "json", "md", "txt"}

# 文件大小限制（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


class FileValidator:
    """文件验证工具类"""
    
    def __init__(
        self, 
        allowed_extensions: Set[str] = None,
        max_file_size: int = None
    ):
        """
        初始化文件验证器
        
        Args:
            allowed_extensions: 允许的文件扩展名集合，默认使用全局配置
            max_file_size: 最大文件大小（字节），默认使用全局配置
        """
        self.allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
        self.max_file_size = max_file_size or MAX_FILE_SIZE
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        获取文件扩展名（不含点号）
        
        Args:
            filename: 文件名
            
        Returns:
            文件扩展名（小写，不含点）
        """
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    def validate_extension(self, filename: str) -> Tuple[bool, str]:
        """
        验证文件扩展名
        
        Args:
            filename: 文件名
            
        Returns:
            (是否合法, 错误信息)
        """
        ext = self.get_file_extension(filename)
        if ext not in self.allowed_extensions:
            return False, f"不支持的文件类型: {ext}，允许的类型: {', '.join(self.allowed_extensions)}"
        return True, ""
    
    def validate_size(self, file_size: int) -> Tuple[bool, str]:
        """
        验证文件大小
        
        Args:
            file_size: 文件大小（字节）
            
        Returns:
            (是否合法, 错误信息)
        """
        if file_size == 0:
            return False, "文件内容为空"
        
        if file_size > self.max_file_size:
            max_mb = self.max_file_size // 1024 // 1024
            return False, f"文件过大，最大允许 {max_mb}MB"
        
        return True, ""
    
    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """
        验证文件名
        
        Args:
            filename: 文件名
            
        Returns:
            (是否合法, 错误信息)
        """
        if not filename:
            return False, "文件名不能为空"
        
        if len(filename) > 255:
            return False, "文件名过长（最大 255 字符）"
        
        return True, ""
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        全面验证文件（文件名 + 扩展名）
        注意：不包括文件大小验证，因为需要先读取文件内容
        
        Args:
            file: FastAPI UploadFile 对象
            
        Returns:
            (是否合法, 错误信息)
        """
        # 验证文件名
        is_valid, error = self.validate_filename(file.filename)
        if not is_valid:
            return False, error
        
        # 验证扩展名
        is_valid, error = self.validate_extension(file.filename)
        if not is_valid:
            return False, error
        
        return True, ""
    
    async def validate_file_full(self, file: UploadFile) -> Tuple[bool, str, bytes]:
        """
        全面验证文件（包括读取并验证大小）
        
        Args:
            file: FastAPI UploadFile 对象
            
        Returns:
            (是否合法, 错误信息, 文件内容)
        """
        # 基础验证
        is_valid, error = self.validate_file(file)
        if not is_valid:
            return False, error, b""
        
        # 读取文件内容
        try:
            content = await file.read()
        except Exception as e:
            return False, f"读取文件失败: {str(e)}", b""
        
        # 验证文件大小
        is_valid, error = self.validate_size(len(content))
        if not is_valid:
            return False, error, b""
        
        return True, "", content

