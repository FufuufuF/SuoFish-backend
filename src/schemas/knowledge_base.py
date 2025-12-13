from ast import List
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")

class KnowledgeBaseDelete(BaseModel):
    id: int = Field(..., description="知识库ID")

class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int = Field(..., description="知识库ID")
    files_names: List[str] = Field(..., description="知识库文件名称列表")
    files_sizes: List[int] = Field(..., description="知识库文件大小列表")
    created_at: datetime = Field(..., description="知识库创建时间")
    updated_at: datetime = Field(..., description="知识库更新时间")
