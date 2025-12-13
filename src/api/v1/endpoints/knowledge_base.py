from fastapi import APIRouter, Depends, Form, File, UploadFile

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.schemas.api_response import APIResponse
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.db.models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus

router = APIRouter()

@router.post("/create", response_model=APIResponse)
async def create_knowledge_base(
    name: str = Form(..., description="知识库名称"),
    description: Optional[str] = Form(None, description="知识库描述"),
    files: List[UploadFile] = File(default=[], description="知识库文件列表"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # TODO: 没有完成文件上传的逻辑
    knowledge_base = KnowledgeBase(
        name=name,
        description=description,
        user_id=user_id,
        status=KnowledgeBaseStatus.UPLOADING
    )
    db.add(knowledge_base)
    await db.commit()
    await db.refresh(knowledge_base)
    return APIResponse(retcode=0, message="success", data=knowledge_base)