import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.conversation import get_conversation_by_id, get_conversations_by_user_id, delete_conversation_by_id
from src.crud.conversation_file import get_files_by_conversation
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.schemas.api_response import APIResponse
from src.schemas.chat import ConversationResponse
from src.services.rag_service import get_rag_service

router = APIRouter()


@router.get("/")
async def get_conversations(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    conversations = await get_conversations_by_user_id(db, user_id)
    # 将 SQLAlchemy 模型转换为 Pydantic 模型
    conversations_data = [ConversationResponse.model_validate(conv) for conv in conversations]
    return APIResponse(retcode=0, message="success", data=conversations_data)


@router.get("/delete/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除会话及其关联的所有资源：
    1. Chroma 向量库中的向量
    2. 磁盘上的物理文件
    3. 数据库中的会话和文件记录（级联删除）
    """
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        return APIResponse(retcode=400, message="Conversation not found")
    if conversation.user_id != user_id:
        return APIResponse(retcode=400, message="Unauthorized access to conversation")
    
    # 1. 删除 Chroma 向量库中该会话的所有向量
    rag_service = get_rag_service()
    try:
        rag_service.delete_conversation_vectors(conversation_id)
    except Exception as e:
        print(f"Failed to delete vectors for conversation {conversation_id}: {e}")
    
    # 2. 获取会话文件并删除物理文件
    conversation_files = await get_files_by_conversation(db, conversation_id)
    for file in conversation_files:
        try:
            if os.path.exists(file.storage_path):
                os.remove(file.storage_path)
        except Exception as e:
            print(f"Failed to delete file {file.storage_path}: {e}")
    
    # 3. 删除会话（数据库中的文件记录会级联删除）
    delete_result = await delete_conversation_by_id(db, conversation_id)
    if delete_result:
        return APIResponse(retcode=0, message="success")
    else:
        return APIResponse(retcode=400, message="Failed to delete conversation")
