# Schema 设计指南

## 问题背景

在开发 API 时，我们经常需要处理三种不同的数据结构：

1. **API 请求体** (Request)：前端发送给后端的数据
2. **数据库模型** (Model/ORM)：数据库中存储的完整数据
3. **API 响应体** (Response)：后端返回给前端的数据

这三者的字段往往**相似但不完全相同**，如果不规范管理，会导致：
- 代码重复
- 命名混乱
- 维护困难
- 数据转换繁琐

## 解决方案：分层 Schema 设计模式

### 1. Schema 分层说明

```
BaseSchema (基础层)
    ├─ CreateSchema (创建层) - POST 请求
    ├─ UpdateSchema (更新层) - PUT/PATCH 请求  
    ├─ InDBSchema (数据库层) - 完整数据库字段
    └─ ResponseSchema (响应层) - API 返回
```

### 2. 各层职责

| Schema 类型 | 用途 | 特点 | 示例 |
|------------|------|------|------|
| **Base** | 共享字段定义 | 包含所有层都需要的核心业务字段 | `ModelConfigBase` |
| **Create** | POST 创建资源 | 包含创建所需的必填字段 + 特殊字段（如 `is_default`） | `ModelConfigCreate` |
| **Update** | PUT/PATCH 更新 | 所有字段都是 `Optional`，支持部分更新 | `ModelConfigUpdate` |
| **InDB** | 数据库完整数据 | 包含所有字段（id、时间戳、外键等） | `ModelConfigInDB` |
| **Response** | API 响应 | 可能隐藏敏感字段或添加计算字段 | `ModelConfigResponse` |

### 3. 实际示例：模型配置

#### 文件结构
```
src/schemas/
  └── model_config.py    # 模型配置相关的所有 schema
```

#### 代码示例

```python
# src/schemas/model_config.py

class ModelConfigBase(BaseModel):
    """基础字段 - 核心业务字段"""
    model_name: str
    display_name: str
    base_url: str
    temperature: float = 0.7
    max_tokens: int = 2048


class ModelConfigCreate(ModelConfigBase):
    """创建请求 - 继承基础字段 + 添加创建专用字段"""
    api_key: str  # 创建时必须提供
    is_default: bool = False  # 创建时才需要的特殊标志


class ModelConfigUpdate(BaseModel):
    """更新请求 - 所有字段可选，支持部分更新"""
    model_name: Optional[str] = None
    display_name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_default: Optional[bool] = None


class ModelConfigInDB(ModelConfigBase):
    """数据库完整数据"""
    id: int  # 数据库自动生成
    user_id: int  # 外键
    api_key: str
    created_at: datetime  # 时间戳
    updated_at: datetime

    model_config = {
        "from_attributes": True  # 支持从 SQLAlchemy 模型创建
    }


class ModelConfigResponse(ModelConfigBase):
    """API 响应 - 可以选择性隐藏或脱敏字段"""
    id: int
    user_id: int
    api_key: str  # 可选：使用 @field_serializer 脱敏
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
```

### 4. 在 API 端点中使用

#### 创建资源
```python
@router.post("/create", response_model=APIResponse)
async def create_model_config(
    config: ModelConfigCreate,  # 使用 Create schema
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 转换为数据库模型
    model_config = create_model_config_from_schema(config, user_id)
    model_config = await crud_add_model_config(db, model_config)
    
    # 转换为响应 schema
    response = ModelConfigResponse.model_validate(model_config)
    return APIResponse(retcode=0, message="success", data=response)
```

#### 获取资源
```python
@router.get("/get", response_model=APIResponse)
async def get_model_configs(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 从数据库获取
    model_configs = await get_model_configs_by_user_id(db, user_id)
    
    # 批量转换为响应 schema
    response_data = [
        ModelConfigResponse.model_validate(config) 
        for config in model_configs
    ]
    return APIResponse(retcode=0, message="success", data=response_data)
```

#### 更新资源
```python
@router.put("/update/{config_id}", response_model=APIResponse)
async def update_model_config(
    config_id: int,
    config: ModelConfigUpdate,  # 使用 Update schema
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 只更新提供的字段
    updated_config = await crud_update_model_config(
        db, 
        config_id, 
        config.model_dump(exclude_unset=True)  # 只包含实际提供的字段
    )
    
    response = ModelConfigResponse.model_validate(updated_config)
    return APIResponse(retcode=0, message="success", data=response)
```

### 5. 辅助函数：统一管理转换逻辑

```python
def create_model_config_from_schema(
    config: ModelConfigCreate, 
    user_id: int
) -> ModelConfig:
    """
    从 Pydantic schema 创建 SQLAlchemy 模型
    集中管理转换逻辑，便于维护
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
```

## 最佳实践

### ✅ 推荐做法

1. **使用继承减少重复**
   ```python
   class Base(BaseModel):
       shared_field: str
   
   class Create(Base):  # 继承 Base
       create_specific_field: str
   ```

2. **Update schema 所有字段都设为 Optional**
   ```python
   class Update(BaseModel):
       field1: Optional[str] = None
       field2: Optional[int] = None
   ```

3. **使用 `model_validate()` 自动转换**
   ```python
   response = ModelConfigResponse.model_validate(db_model)
   ```

4. **使用 `exclude_unset=True` 获取部分更新字段**
   ```python
   update_data = config.model_dump(exclude_unset=True)
   ```

5. **按功能模块组织 schema 文件**
   ```
   schemas/
     ├── model_config.py   # 模型配置相关
     ├── chat.py          # 聊天相关
     ├── conversation.py  # 会话相关
     └── user.py         # 用户相关
   ```

### ❌ 避免的做法

1. **不要在一个文件里混合多个模块的 schema**
   ```python
   # ❌ 不好
   # llm_config.py 里同时包含 ModelConfig 和 Chat 的 schema
   ```

2. **不要在端点里手动逐字段赋值**
   ```python
   # ❌ 不好
   model = Model(
       field1=request.field1,
       field2=request.field2,
       # ... 很多字段
   )
   
   # ✅ 好
   model = create_model_from_schema(request, extra_fields)
   ```

3. **不要直接使用数据库模型作为请求体**
   ```python
   # ❌ 不好
   @router.post("/create")
   async def create(config: ModelConfig):  # 数据库模型
       pass
   
   # ✅ 好
   @router.post("/create")
   async def create(config: ModelConfigCreate):  # 请求 schema
       pass
   ```

## 命名规范

| 场景 | 命名 | 示例 |
|------|------|------|
| 基础字段 | `{Resource}Base` | `ModelConfigBase` |
| 创建请求 | `{Resource}Create` | `ModelConfigCreate` |
| 更新请求 | `{Resource}Update` | `ModelConfigUpdate` |
| 数据库模型 | `{Resource}InDB` | `ModelConfigInDB` |
| API 响应 | `{Resource}Response` | `ModelConfigResponse` |
| 列表响应 | `{Resource}ListResponse` | `ModelConfigListResponse` |

## 数据流转图

```
Frontend                Backend                     Database
   │                       │                            │
   │  POST /create         │                            │
   ├──────────────────────>│                            │
   │  ModelConfigCreate    │                            │
   │                       │                            │
   │                       │ create_from_schema()       │
   │                       ├───────────────┐            │
   │                       │               │            │
   │                       │<──────────────┘            │
   │                       │  ModelConfig (ORM)         │
   │                       │                            │
   │                       │  save to DB                │
   │                       ├───────────────────────────>│
   │                       │                            │
   │                       │<───────────────────────────┤
   │                       │  ModelConfig (ORM)         │
   │                       │                            │
   │                       │ model_validate()           │
   │                       ├───────────────┐            │
   │                       │               │            │
   │                       │<──────────────┘            │
   │                       │  ModelConfigResponse       │
   │                       │                            │
   │  ModelConfigResponse  │                            │
   │<──────────────────────┤                            │
   │                       │                            │
```

## 总结

这种分层设计模式的优势：

1. **清晰的职责分离**：每个 schema 只负责一个场景
2. **减少代码重复**：通过继承复用共享字段
3. **便于维护**：修改某个层级不影响其他层级
4. **类型安全**：Pydantic 提供完整的类型检查
5. **自动验证**：FastAPI + Pydantic 自动验证请求数据
6. **易于测试**：每个 schema 都可以独立测试
7. **文档友好**：FastAPI 自动生成准确的 API 文档

记住核心原则：**不同场景使用不同的 schema，通过继承和组合来复用代码**。

