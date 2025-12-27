from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from datetime import datetime
from src.db.models.model_config import ModelConfig


async def add_model_config(db: AsyncSession, model_config: ModelConfig) -> ModelConfig:
    """添加新的模型配置"""
    db.add(model_config)
    await db.commit()
    await db.refresh(model_config)
    return model_config


async def get_model_configs_by_user_id(db: AsyncSession, user_id: int) -> List[ModelConfig]:
    """获取用户的所有模型配置"""
    result = await db.execute(select(ModelConfig).filter(ModelConfig.user_id == user_id))
    return result.scalars().all()


async def get_model_config_by_id(db: AsyncSession, config_id: int) -> Optional[ModelConfig]:
    """根据 ID 获取模型配置"""
    result = await db.execute(select(ModelConfig).filter(ModelConfig.id == config_id))
    return result.scalar_one_or_none()


async def update_model_config(
    db: AsyncSession, 
    id: int, 
    model_name: str,
    display_name: str,
    base_url: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> Optional[ModelConfig]:
    """
    更新模型配置（全量更新）
    
    Args:
        db: 数据库会话
        config_id: 配置 ID
        model_name: 模型名称
        display_name: 显示名称
        base_url: API 基础 URL
        api_key: API 密钥
        temperature: 温度参数
        max_tokens: 最大令牌数
        
    Returns:
        更新后的模型配置，如果不存在则返回 None
    """
    model_config = await get_model_config_by_id(db, id)
    if not model_config:
        return None
    
    # 更新所有字段
    model_config.model_name = model_name
    model_config.display_name = display_name
    model_config.base_url = base_url
    model_config.api_key = api_key
    model_config.temperature = temperature
    model_config.max_tokens = max_tokens
    model_config.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(model_config)
    return model_config


async def delete_model_config(db: AsyncSession, id: int) -> bool:
    """
    删除模型配置
    
    Args:
        db: 数据库会话
        config_id: 配置 ID
        
    Returns:
        删除成功返回 True，配置不存在返回 False
    """
    # 避免循环导入
    from src.db.models.user import User
    from sqlalchemy import update

    model_config = await get_model_config_by_id(db, id)
    if not model_config:
        return False
    
    # 在删除模型配置之前，先将引用该配置的用户的 default_model_config_id 设置为 None
    await db.execute(
        update(User)
        .where(User.default_model_config_id == id)
        .values(default_model_config_id=None)
    )
    
    await db.delete(model_config)
    await db.commit()
    return True