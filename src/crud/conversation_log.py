from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.conversation_log import ConversationLogSession, ConversationLogRound


async def get_or_create_log_session(
    db: AsyncSession,
    conversation_id: int,
    user_id: int
) -> ConversationLogSession:
    result = await db.execute(
        select(ConversationLogSession)
        .filter(ConversationLogSession.conversation_id == conversation_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        new_session = ConversationLogSession(
            conversation_id=conversation_id,
            user_id=user_id
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        session = new_session
    return session


async def create_log_round(
    db: AsyncSession,
    session_id: int,
    round_number: int,
    user_message: str,
    assistant_message: str,
    files_result: Optional[dict] = None,
    rag_results: Optional[dict] = None,
    error: Optional[str] = None,
    save_error: Optional[str] = None
) -> ConversationLogRound:
    """创建一轮对话日志"""
    new_round = ConversationLogRound(
        session_id=session_id,
        round_number=round_number,
        user_message=user_message,
        assistant_message=assistant_message,
        files_result=files_result,
        rag_results=rag_results,
        error=error,
        save_error=save_error
    )
    db.add(new_round)
    await db.commit()
    await db.refresh(new_round)
    return new_round


async def get_log_rounds_by_session(
    db: AsyncSession,
    session_id: int
) -> List[ConversationLogRound]:
    """获取某个会话日志的所有轮次"""
    result = await db.execute(
        select(ConversationLogRound)
        .filter(ConversationLogRound.session_id == session_id)
        .order_by(ConversationLogRound.round_number.asc())  # 按轮次升序排序
    )
    return list(result.scalars().all())


async def get_log_session_by_conversation(
    db: AsyncSession,
    conversation_id: int
) -> Optional[ConversationLogSession]:
    """通过 conversation_id 查询会话日志"""
    result = await db.execute(
        select(ConversationLogSession)
        .filter(ConversationLogSession.conversation_id == conversation_id)
    )
    return result.scalar_one_or_none()


async def update_log_session_stats(
    db: AsyncSession,
    session_id: int,
    has_error: bool = False
) -> Optional[ConversationLogSession]:
    """更新会话日志的统计信息"""
    result = await db.execute(
        select(ConversationLogSession)
        .filter(ConversationLogSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if session:
        session.total_rounds += 1  # 轮次数加 1
        if has_error:
            session.has_errors = True  # 标记为有错误
        await db.commit()
        await db.refresh(session)
    
    return session

