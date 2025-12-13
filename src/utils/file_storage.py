"""
文件物理存储工具 - 提供文件的磁盘存储操作
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple

import aiofiles


# 文件存储根目录
UPLOAD_DIR = Path("uploads")


class FileStorage:
    """文件物理存储工具类"""
    
    def __init__(self, base_dir: Path = None):
        """
        初始化文件存储工具
        
        Args:
            base_dir: 基础存储目录，默认使用全局配置
        """
        self.base_dir = base_dir or UPLOAD_DIR
        # 确保基础目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        生成唯一文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            带唯一ID的文件名: {uuid}_{original_filename}
        """
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = original_filename.replace(" ", "_")
        return f"{unique_id}_{safe_filename}"
    
    def generate_storage_path(
        self, 
        entity_type: str,  # "conversation" 或 "kb"
        entity_id: int, 
        original_filename: str
    ) -> str:
        """
        生成存储路径
        
        格式: uploads/{entity_type}_{entity_id}/{date}/{uuid}_{original_filename}
        例如: 
            - uploads/conversation_123/2025/12/13/a1b2c3d4_document.pdf
            - uploads/kb_45/2025/12/13/a1b2c3d4_manual.docx
        
        Args:
            entity_type: 实体类型（"conversation" 或 "kb"）
            entity_id: 实体 ID
            original_filename: 原始文件名
            
        Returns:
            相对存储路径
        """
        date_str = datetime.utcnow().strftime("%Y/%m/%d")
        unique_filename = self.generate_unique_filename(original_filename)
        
        return str(
            self.base_dir / f"{entity_type}_{entity_id}" / date_str / unique_filename
        )
    
    async def save_file(
        self, 
        content: bytes, 
        storage_path: str
    ) -> Tuple[bool, str]:
        """
        保存文件到磁盘
        
        Args:
            content: 文件内容（字节）
            storage_path: 存储路径
            
        Returns:
            (是否成功, 错误信息)
        """
        # 确保目录存在
        file_path = Path(storage_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 异步写入文件
        try:
            async with aiofiles.open(storage_path, "wb") as f:
                await f.write(content)
            return True, ""
        except Exception as e:
            return False, f"文件保存失败: {str(e)}"
    
    async def delete_file(self, storage_path: str) -> bool:
        """
        删除磁盘上的文件
        
        Args:
            storage_path: 存储路径
            
        Returns:
            是否成功删除
        """
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
                
                # 尝试删除空目录（递归向上）
                parent = Path(storage_path).parent
                try:
                    while parent != self.base_dir and parent.exists():
                        if not any(parent.iterdir()):  # 目录为空
                            parent.rmdir()
                            parent = parent.parent
                        else:
                            break
                except Exception:
                    pass  # 删除空目录失败不影响主流程
                
            return True
        except Exception:
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            storage_path: 存储路径
            
        Returns:
            文件是否存在
        """
        return Path(storage_path).exists()
    
    def get_file_path(self, storage_path: str) -> Path:
        """
        获取文件的 Path 对象
        
        Args:
            storage_path: 存储路径
            
        Returns:
            Path 对象
        """
        return Path(storage_path)

