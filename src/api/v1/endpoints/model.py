from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.model_config import ModelConfig
from src.schemas.llm_config import ModelConfigResponse
from src.utils.authentic import get_current_user
from src.api.deps import get_db
from src.crud.model import add_model_config, get_model_configs_by_user_id
from src.schemas.api_response import APIResponse
from src.crud.user import get_user_default_model_config, set_user_default_model_config

router = APIRouter()

@router.post("/")
async def add_model_config(
    model_name: str,
    display_name: str,
    base_url: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    is_default: bool = False,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    model_config = ModelConfig(
        model_name=model_name,
        display_name=display_name,
        user_id=user_id,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    model_config = await add_model_config(db, model_config)
    if is_default:
        await set_user_default_model_config(db, user_id, model_config.id)
    response = ModelConfigResponse.model_validate(model_config)
    return APIResponse(retcode=0, message="success", data=response)

@router.get("/")
async def get_model_configs(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    model_configs = await get_model_configs_by_user_id(db, user_id)
    model_configs_data = [ModelConfigResponse.model_validate(model_config) for model_config in model_configs]
    default_model_id = await get_user_default_model_config(db, user_id) 
    return APIResponse(retcode=0, message="success", data={
        "model_configs": model_configs_data,
        "default_model_id": default_model_id,
    })