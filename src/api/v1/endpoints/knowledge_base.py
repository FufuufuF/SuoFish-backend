"""
知识库 API 端点
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.api_response import APIResponse
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.db.models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus
from src.services.knowledge_base_file_service import KnowledgeBaseFileService
from src.services.rag_service import get_rag_service


router = APIRouter()


async def process_knowledge_base_files_background(
    knowledge_base_id: int,
    db: AsyncSession
):
    """
    后台任务：处理知识库文件（chunk + embed）
    
    Args:
        knowledge_base_id: 知识库 ID
        db: 数据库会话
    """
    from src.crud import knowledge_base as kb_crud
    from src.crud import knowledge_base_file as kb_file_crud
    
    try:
        # 1. 更新知识库状态为 CHUNKING
        kb = await kb_crud.update_knowledge_base_status(
            db, 
            knowledge_base_id, 
            KnowledgeBaseStatus.CHUNKING
        )
        if not kb:
            return
        
        # 2. 获取所有文件
        files = await kb_file_crud.get_files_by_knowledge_base(db, knowledge_base_id)
        
        # 3. 对每个文件进行 chunk 和 embed
        rag_service = get_rag_service()
        file_list = []
        
        for file in files:
            try:
                # Embed 文件
                result = rag_service.embed_knowledge_base_file(
                    file_path=Path(file.file_path),
                    file_id=file.id,
                    knowledge_base_id=knowledge_base_id,
                    user_id=kb.user_id,
                    file_name=file.file_name
                )
                print(f"文件 {file.file_name} 处理完成: {result.chunk_count} 个分块")
                
                # 收集文件信息
                file_list.append({
                    "file_id": file.id,
                    "file_name": file.file_name
                })
            except Exception as e:
                print(f"文件 {file.file_name} 处理失败: {str(e)}")
                continue
        
        # 4. 更新知识库的文件列表
        await kb_crud.update_knowledge_base_file_list(db, knowledge_base_id, file_list)
        
        # 5. 更新知识库状态为 PUBLISHED
        await kb_crud.update_knowledge_base_status(
            db,
            knowledge_base_id,
            KnowledgeBaseStatus.PUBLISHED
        )
        
        print(f"知识库 {knowledge_base_id} 处理完成")
        
    except Exception as e:
        print(f"知识库 {knowledge_base_id} 处理失败: {str(e)}")
        # 更新状态为错误（暂时设置回 UPLOADING，后续可以添加 ERROR 状态）
        try:
            await kb_crud.update_knowledge_base_status(
                db,
                knowledge_base_id,
                KnowledgeBaseStatus.UPLOADING
            )
        except Exception:
            pass


@router.post("/create", response_model=APIResponse)
async def create_knowledge_base(
    name: str = Form(..., min_length=1, max_length=100, description="知识库名称"),
    description: Optional[str] = Form(None, max_length=500, description="知识库描述"),
    files: List[UploadFile] = File(..., description="知识库文件列表"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建知识库
    
    流程：
    1. 验证文件
    2. 创建知识库记录（状态：UPLOADING）
    3. 保存文件到磁盘和数据库
    4. 启动后台任务：chunk + embed（更新状态：CHUNKING -> PUBLISHED）
    """
    from src.crud import knowledge_base as kb_crud
    
    # 1. 验证文件数量
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="至少需要上传一个文件")
    
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="最多只能上传 20 个文件")
    
    # 2. 创建知识库记录
    knowledge_base_obj = KnowledgeBase(
        name=name,
        description=description,
        user_id=user_id,
        status=KnowledgeBaseStatus.UPLOADING.value,
        file_list=[]
    )
    knowledge_base = await kb_crud.create_knowledge_base(db, knowledge_base_obj)
    
    # 3. 保存文件
    file_service = KnowledgeBaseFileService(db)
    saved_files, errors = await file_service.save_files(files, knowledge_base.id)
    
    # 4. 如果所有文件都失败，删除知识库
    if not saved_files:
        await kb_crud.delete_knowledge_base(db, knowledge_base.id)
        raise HTTPException(
            status_code=400,
            detail=f"所有文件保存失败: {'; '.join(errors)}"
        )
    
    # 5. 启动后台任务处理文件
    # 注意：需要创建新的数据库会话用于后台任务
    from src.api.deps import get_db
    async def background_task():
        async for bg_db in get_db():
            try:
                await process_knowledge_base_files_background(
                    knowledge_base.id,
                    bg_db
                )
            finally:
                await bg_db.close()
            break
    
    asyncio.create_task(background_task())
    
    # 6. 返回结果
    return APIResponse(
        retcode=0,
        message="知识库创建成功，文件正在后台处理中",
        data={
            "id": knowledge_base.id,
            "name": knowledge_base.name,
            "description": knowledge_base.description,
            "status": knowledge_base.status,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )


@router.get("/list", response_model=APIResponse)
async def list_knowledge_bases(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有知识库列表"""
    from src.crud import knowledge_base as kb_crud
    
    kbs = await kb_crud.get_knowledge_bases_by_user(db, user_id)
    
    return APIResponse(
        retcode=0,
        message="success",
        data={
            "knowledge_bases": [
                {
                    "id": kb.id,
                    "name": kb.name,
                    "description": kb.description,
                    "status": kb.status,
                    "created_at": kb.created_at.isoformat(),
                    "updated_at": kb.updated_at.isoformat()
                }
                for kb in kbs
            ],            
        },
    )


@router.get("/{knowledge_base_id}", response_model=APIResponse)
async def get_knowledge_base(
    knowledge_base_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库详情"""
    from src.crud import knowledge_base as kb_crud
    from src.crud import knowledge_base_file as kb_file_crud
    
    # 获取知识库
    kb = await kb_crud.get_knowledge_base_by_id(db, knowledge_base_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 验证权限
    if kb.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此知识库")
    
    # 获取文件列表
    files = await kb_file_crud.get_files_by_knowledge_base(db, knowledge_base_id)
    
    return APIResponse(
        retcode=0,
        message="success",
        data={
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "status": kb.status,
            "created_at": kb.created_at.isoformat(),
            "updated_at": kb.updated_at.isoformat(),
        }
    )


@router.delete("/{knowledge_base_id}", response_model=APIResponse)
async def delete_knowledge_base(
    knowledge_base_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除知识库"""
    from src.crud import knowledge_base as kb_crud
    
    # 获取知识库
    kb = await kb_crud.get_knowledge_base_by_id(db, knowledge_base_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 验证权限
    if kb.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此知识库")
    
    # 删除文件
    file_service = KnowledgeBaseFileService(db)
    await file_service.delete_all_files(knowledge_base_id)
    
    # 删除向量
    rag_service = get_rag_service()
    rag_service.delete_knowledge_base_vectors(knowledge_base_id)
    
    # 删除知识库记录
    success = await kb_crud.delete_knowledge_base(db, knowledge_base_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="删除知识库失败")
    
    return APIResponse(retcode=0, message="知识库删除成功", data=None)
