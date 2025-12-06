from typing import Optional
import json

from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService
from src.utils.authentic import get_current_user
from src.api.deps import get_db

router = APIRouter()


@router.post("/")
async def chat(
    user_message: str = Form(..., description="用户消息内容"),
    conversation_id: Optional[int] = Form(None, description="会话ID，不传则创建新会话"),
    knowledge_base_ids: Optional[str] = Form(None, description="知识库ID列表，JSON格式如 [1,2,3]"),
    files: list[UploadFile] = File(default=[], description="上传的文件列表"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    聊天接口 - 流式返回 LLM 响应，支持文件上传和 RAG 检索
    
    请求格式: multipart/form-data
    - user_message: 用户消息 (必填)
    - conversation_id: 会话ID (可选，不传则创建新会话)
    - knowledge_base_ids: 知识库ID列表 (可选，JSON格式如 "[1,2,3]")
    - files: 文件列表 (可选，支持 .pdf/.docx/.pptx)
    
    返回 NDJSON 格式的流式响应:
    - {"token": "..."} - LLM 生成的 token
    - {"error": "..."} - 错误信息  
    - {"metadata": {...}} - 完成后的元数据
    - {"files": {...}} - 上传文件的处理结果
    - {"rag_results": {...}} - RAG 检索结果
    """
    # 解析 knowledge_base_ids
    kb_ids = None
    if knowledge_base_ids:
        try:
            kb_ids = json.loads(knowledge_base_ids)
            if not isinstance(kb_ids, list):
                kb_ids = None
        except json.JSONDecodeError:
            kb_ids = None
    
    chat_service = ChatService(db)
    return StreamingResponse(
        chat_service.process_chat(
            user_message=user_message,
            user_id=user_id,
            conversation_id=conversation_id,
            files=files,
            knowledge_base_ids=kb_ids
        ),
        media_type="application/x-ndjson"
    )
