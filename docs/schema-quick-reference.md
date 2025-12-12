# Schema 重构快速参考

## 📌 核心概念

**问题**：前端请求体、数据库模型、后端响应三者字段相似但不同，如何管理？

**解决方案**：分层 Schema 设计模式

```
前端 JSON → CreateSchema → 数据库 ORM Model → ResponseSchema → 前端 JSON
```

---

## 🎯 五层架构

| Schema | 用途 | 字段特点 | 示例 |
|--------|------|---------|------|
| **Base** | 共享字段 | 核心业务字段 | `model_name`, `display_name` |
| **Create** | POST 请求 | 必填字段 + 特殊标志 | `+ api_key`, `+ is_default` |
| **Update** | PUT/PATCH | 全部 Optional | `Optional[model_name]` |
| **InDB** | 数据库完整 | 所有字段（含 id、时间戳） | `+ id`, `+ created_at` |
| **Response** | API 返回 | 可脱敏、可添加计算字段 | `api_key: masked` |

---

## 📝 代码模板

### 1. Schema 定义（src/schemas/xxx.py）

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 1️⃣ 基础层
class ResourceBase(BaseModel):
    """共享的核心字段"""
    name: str
    description: Optional[str] = None

# 2️⃣ 创建层
class ResourceCreate(ResourceBase):
    """POST 创建"""
    api_key: str
    is_default: bool = False

# 3️⃣ 更新层
class ResourceUpdate(BaseModel):
    """PUT/PATCH 更新"""
    name: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = None
    is_default: Optional[bool] = None

# 4️⃣ 数据库层
class ResourceInDB(ResourceBase):
    """完整数据库字段"""
    id: int
    user_id: int
    api_key: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

# 5️⃣ 响应层
class ResourceResponse(ResourceBase):
    """API 返回"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

# 6️⃣ 列表响应（可选）
class ResourceListResponse(BaseModel):
    items: list[ResourceResponse]
    total: int
    default_id: Optional[int] = None
```

### 2. 辅助函数（在 endpoint 文件中）

```python
def create_resource_from_schema(
    data: ResourceCreate,
    user_id: int
) -> Resource:
    """统一管理 Schema → ORM 转换"""
    now = datetime.now()
    return Resource(
        name=data.name,
        description=data.description,
        user_id=user_id,
        api_key=data.api_key,
        created_at=now,
        updated_at=now,
    )
```

### 3. API 端点使用

```python
# POST 创建
@router.post("/create", response_model=APIResponse)
async def create_resource(
    data: ResourceCreate,  # ✅ 使用 Create
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resource = create_resource_from_schema(data, user_id)
    resource = await crud_add_resource(db, resource)
    
    response = ResourceResponse.model_validate(resource)  # ✅ 自动转换
    return APIResponse(retcode=0, message="success", data=response)

# GET 查询
@router.get("/get", response_model=APIResponse)
async def get_resources(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resources = await crud_get_resources(db, user_id)
    
    response_list = [
        ResourceResponse.model_validate(r)  # ✅ 批量转换
        for r in resources
    ]
    return APIResponse(retcode=0, message="success", data=response_list)

# PUT 更新
@router.put("/update/{resource_id}", response_model=APIResponse)
async def update_resource(
    resource_id: int,
    data: ResourceUpdate,  # ✅ 使用 Update
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 只更新提供的字段
    update_data = data.model_dump(exclude_unset=True)  # ✅ 关键！
    updated = await crud_update_resource(db, resource_id, update_data)
    
    response = ResourceResponse.model_validate(updated)
    return APIResponse(retcode=0, message="success", data=response)
```

---

## ✅ 最佳实践

### DO ✅
- ✅ 使用继承减少重复：`Create(Base)`
- ✅ Update 所有字段设为 Optional
- ✅ 使用 `model_validate()` 自动转换
- ✅ 使用 `exclude_unset=True` 部分更新
- ✅ 按模块组织文件：`model_config.py`, `chat.py`
- ✅ 添加辅助函数统一管理转换逻辑
- ✅ 使用 Field() 添加描述和验证

### DON'T ❌
- ❌ 不要在一个文件里混合多个模块
- ❌ 不要手动逐字段赋值（超过 3 个字段）
- ❌ 不要直接用 ORM 模型作为请求体
- ❌ 不要在 Response 中返回敏感信息（密码、完整 API key）
- ❌ 不要忘记 `from_attributes = True`（从 ORM 转换时）

---

## 🔄 数据转换方法

| 场景 | 方法 | 示例 |
|------|------|------|
| Schema → ORM | 手动或辅助函数 | `create_xxx_from_schema(data, extra)` |
| ORM → Schema | `model_validate()` | `Response.model_validate(orm_obj)` |
| Schema → Dict | `model_dump()` | `data.model_dump()` |
| 部分更新 | `exclude_unset=True` | `data.model_dump(exclude_unset=True)` |
| 批量转换 | 列表推导式 | `[Response.model_validate(x) for x in items]` |

---

## 📁 推荐文件结构

```
src/schemas/
├── __init__.py
├── api_response.py      # 通用 API 响应包装
├── model_config.py      # 模型配置（已完成 ✅）
├── chat.py             # 聊天请求（已整理 ✅）
├── conversation.py     # 会话管理（待创建）
├── message.py          # 消息（待创建）
├── user.py            # 用户（待创建）
├── auth.py            # 认证（待创建）
└── file.py            # 文件上传（待创建）
```

---

## 🎓 命名规范速查

| 后缀 | 含义 | 典型字段 |
|------|------|---------|
| `Base` | 基础共享字段 | 核心业务字段 |
| `Create` | POST 创建 | Base + 创建必需字段 |
| `Update` | PUT/PATCH 更新 | 全部 Optional |
| `InDB` | 数据库完整 | 所有字段 + id + 时间戳 |
| `Response` | API 返回 | InDB - 敏感字段 |
| `ListResponse` | 列表返回 | `items: list[Response]` |

---

## 💡 常见问题

### Q1: Create 和 Update 有什么区别？
**A**: Create 字段通常是必填，Update 所有字段都是 Optional（支持部分更新）

### Q2: 什么时候用 InDB，什么时候用 Response？
**A**: InDB 表示数据库完整字段（内部使用），Response 是对外 API 返回（可能隐藏敏感信息）

### Q3: 为什么要用辅助函数转换？
**A**: 集中管理转换逻辑，方便维护。如果字段少（<3个）可以直接赋值。

### Q4: model_validate 和 parse_obj 有什么区别？
**A**: `model_validate()` 是 Pydantic v2 的新方法，`parse_obj()` 已废弃。

### Q5: 如何脱敏敏感字段（如 API key）？
**A**: 使用 `@field_serializer` 装饰器：
```python
from pydantic import field_serializer

class Response(BaseModel):
    api_key: str
    
    @field_serializer('api_key')
    def mask_api_key(self, value: str) -> str:
        return value[:4] + "*" * (len(value) - 8) + value[-4:]
```

---

## 📚 相关文档

- 详细设计指南：`docs/schema-design-guide.md`
- 迁移清单：`docs/schema-refactor-checklist.md`
- Pydantic 官方文档：https://docs.pydantic.dev/

---

**记住**：不同场景用不同 Schema，通过继承复用代码！🚀

