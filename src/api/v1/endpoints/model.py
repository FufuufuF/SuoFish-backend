from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.model_config import ModelConfig
from src.schemas.model_config import (
    ModelConfigResponse,
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigDelete,
    ModelConfigListResponse,
)
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.crud.model import (
    add_model_config as crud_add_model_config, 
    get_model_configs_by_user_id as crud_get_model_configs_by_user_id,
    get_model_config_by_id as crud_get_model_config_by_id,
    update_model_config as crud_update_model_config,
    delete_model_config as crud_delete_model_config,
)
from src.schemas.api_response import APIResponse
from src.crud.user import get_user_default_model_config_id, set_user_default_model_config

router = APIRouter()


def create_model_config_from_schema(config: ModelConfigCreate, user_id: int) -> ModelConfig:
    """
    从 Pydantic schema 创建 SQLAlchemy 模型
    这个辅助函数集中管理从请求体到数据库模型的转换
    """
    now = datetime.now()
    return ModelConfig(
        model_name=config.model_name,
        display_name=config.display_name,
        user_id=user_id,
        base_url=config.base_url,
        api_key=config.api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        created_at=now,
        updated_at=now,
    )


@router.post("/create", response_model=APIResponse)
async def create_model_config(
    config: ModelConfigCreate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新的模型配置
    
    - **model_name**: 模型名称（如 gpt-4）
    - **display_name**: 显示名称
    - **base_url**: API 基础 URL
    - **api_key**: API 密钥
    - **temperature**: 温度参数 (0-2)
    - **max_tokens**: 最大令牌数
    - **is_default**: 是否设为默认模型
    """
    # 使用辅助函数创建模型
    model_config = create_model_config_from_schema(config, user_id)
    model_config = await crud_add_model_config(db, model_config)
    
    # 如果需要设为默认，更新用户的默认配置
    if config.is_default:
        await set_user_default_model_config(db, user_id, model_config.id)
    
    # 使用 Pydantic 的 model_validate 自动转换
    response = ModelConfigResponse.model_validate(model_config)
    return APIResponse(retcode=0, message="success", data=response)


@router.get("/get", response_model=APIResponse)
async def get_model_configs(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户的所有模型配置及默认模型 ID
    """
    model_configs = await crud_get_model_configs_by_user_id(db, user_id)
    model_configs_data = [
        ModelConfigResponse.model_validate(config) 
        for config in model_configs
    ]
    default_model_id = await get_user_default_model_config_id(db, user_id)
    
    # 使用专门的列表响应 schema
    list_response = ModelConfigListResponse(
        model_configs=model_configs_data,
        default_model_id=default_model_id,
    )
    
    return APIResponse(retcode=0, message="success", data=list_response)


@router.post("/update", response_model=APIResponse)
async def update_model_config(
    config: ModelConfigUpdate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新模型配置（全量更新）
    
    前端需要提交完整的配置数据，包括所有字段
    """
    # 1. 获取指定的配置
    model_config = await crud_get_model_config_by_id(db, config.id)
    if not model_config:
        return APIResponse(retcode=1, message="Model config not found", data=None)
    
    # 2. 验证配置是否属于当前用户
    if model_config.user_id != user_id:
        return APIResponse(retcode=403, message="Unauthorized access to this config", data=None)
    
    # 3. 更新配置（全量更新）
    updated_config = await crud_update_model_config(
        db=db,
        id=config.id,
        model_name=config.model_name,
        display_name=config.display_name,
        base_url=config.base_url,
        api_key=config.api_key,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    
    if not updated_config:
        return APIResponse(retcode=1, message="Failed to update config", data=None)
    
    # 4. 如果需要设为默认，更新用户的默认配置
    if config.is_default is True:
        await set_user_default_model_config(db, user_id, config.id)
    
    # 5. 返回更新后的配置
    response = ModelConfigResponse.model_validate(updated_config)
    return APIResponse(retcode=0, message="success", data=response)


@router.post("/delete/", response_model=APIResponse)
async def delete_model_config(
    request: ModelConfigDelete,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除模型配置
    
    注意：如果删除的是默认配置，会自动清空用户的默认配置
    """
    # 1. 获取指定的配置
    model_config = await crud_get_model_config_by_id(db, request.id)
    if not model_config:
        return APIResponse(retcode=1, message="Model config not found", data=None)
    
    # 2. 验证配置是否属于当前用户
    if model_config.user_id != user_id:
        return APIResponse(retcode=403, message="Unauthorized access to this config", data=None)
    
    # 3. 检查是否是默认配置
    default_model_id = await get_user_default_model_config_id(db, user_id)
    is_default = (default_model_id == request.id)
    
    # 4. 删除配置
    success = await crud_delete_model_config(db, request.id)
    if not success:
        return APIResponse(retcode=1, message="Failed to delete config", data=None)
    
    # 5. 如果删除的是默认配置，清空用户的默认配置
    if is_default:
        await set_user_default_model_config(db, user_id, None)
    
    return APIResponse(retcode=0, message="Model config deleted successfully", data=None)

