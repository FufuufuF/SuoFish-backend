# Schema 重构迁移清单

## 已完成 ✅

### 1. 模型配置模块
- [x] 创建 `src/schemas/model_config.py`
- [x] 定义分层 schema：
  - `ModelConfigBase`
  - `ModelConfigCreate`
  - `ModelConfigUpdate`
  - `ModelConfigInDB`
  - `ModelConfigResponse`
  - `ModelConfigListResponse`
- [x] 更新 `src/api/v1/endpoints/model.py`
- [x] 添加辅助函数 `create_model_config_from_schema()`
- [x] 保留 `src/schemas/llm_config.py` 作为兼容层（重新导出）

### 2. 聊天模块
- [x] 整理 `src/schemas/chat.py`
- [x] 迁移 `ChatMetadata` 到正确位置

## 待重构模块 📋

### 3. 会话（Conversation）模块

#### 当前状态
```python
# src/schemas/chat.py
class ConversationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
```

#### 需要的 Schema
```python
# src/schemas/conversation.py (新建)
class ConversationBase(BaseModel):
    name: str

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    name: Optional[str] = None

class ConversationInDB(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
```

#### 需要更新的文件
- [ ] 创建 `src/schemas/conversation.py`
- [ ] 更新 `src/api/v1/endpoints/conversations.py`
- [ ] 从 `src/schemas/chat.py` 移除 `ConversationResponse`

---

### 4. 消息（Message）模块

#### 当前状态
```python
# src/schemas/chat.py
class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    created_at: datetime
```

#### 需要的 Schema
```python
# src/schemas/message.py (新建)
class MessageBase(BaseModel):
    content: str
    role: str  # 或使用 Enum

class MessageCreate(MessageBase):
    conversation_id: int

class MessageInDB(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    model_config = {"from_attributes": True}

class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}

class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
```

#### 需要更新的文件
- [ ] 创建 `src/schemas/message.py`
- [ ] 更新 `src/api/v1/endpoints/messages.py`
- [ ] 从 `src/schemas/chat.py` 移除 `MessageResponse`

---

### 5. 用户（User）模块

#### 需要检查
- [ ] 检查 `src/db/models/user.py` 的字段
- [ ] 创建 `src/schemas/user.py`（如果还没有）
- [ ] 定义用户相关的 schema：
  - `UserBase`
  - `UserCreate` (注册)
  - `UserLogin` (登录)
  - `UserUpdate` (更新资料)
  - `UserInDB` (包含密码 hash)
  - `UserResponse` (不包含密码)

---

### 6. 认证（Auth）模块

#### 需要的 Schema
```python
# src/schemas/auth.py (新建或重构)
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

---

### 7. 文件上传模块

#### 需要的 Schema
```python
# src/schemas/file.py (新建)
class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    file_path: str
    file_size: int
    upload_time: datetime

class FileListResponse(BaseModel):
    files: list[FileUploadResponse]
    total: int
```

---

## 重构步骤模板

对每个模块执行以下步骤：

### Step 1: 分析现有代码
```bash
# 找出所有相关的 schema 定义
grep -r "class.*Response\|class.*Create" src/schemas/
```

### Step 2: 创建新的 schema 文件
```python
# src/schemas/{module}.py
"""
{模块名}相关的 Pydantic Schema
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base -> Create -> Update -> InDB -> Response
```

### Step 3: 更新 API 端点
```python
# 导入新的 schema
from src.schemas.{module} import (
    {Module}Create,
    {Module}Update,
    {Module}Response,
)

# 添加辅助函数
def create_{module}_from_schema(data: {Module}Create, **extra) -> {Module}:
    """转换逻辑"""
    pass

# 更新端点函数签名和返回类型
@router.post("/create", response_model=APIResponse)
async def create_{module}(
    data: {Module}Create,
    ...
):
    pass
```

### Step 4: 更新导入
```bash
# 全局搜索旧的导入语句
grep -r "from src.schemas.chat import.*Response" src/
```

### Step 5: 测试
- [ ] 测试 POST 创建
- [ ] 测试 GET 查询
- [ ] 测试 PUT 更新
- [ ] 测试 DELETE 删除
- [ ] 检查 API 文档 (Swagger UI)

---

## 命名规范检查清单

每个模块应该有：

- [ ] `{Resource}Base` - 基础字段
- [ ] `{Resource}Create` - 创建请求
- [ ] `{Resource}Update` - 更新请求 (所有字段 Optional)
- [ ] `{Resource}InDB` - 数据库完整字段
- [ ] `{Resource}Response` - API 响应
- [ ] `{Resource}ListResponse` - 列表响应（如果需要）

---

## 注意事项

1. **向后兼容**：
   - 保留旧的导入路径，使用重新导出
   - 添加废弃警告注释

2. **渐进式重构**：
   - 一次重构一个模块
   - 每次重构后运行测试
   - 确保 API 行为不变

3. **文档更新**：
   - 更新 API 文档注释
   - 更新 README
   - 添加示例代码

4. **代码审查要点**：
   - Schema 层级是否清晰
   - 字段验证是否完整
   - 类型注解是否准确
   - 是否有重复代码

---

## 最终目标结构

```
src/schemas/
├── __init__.py
├── api_response.py       # 通用响应
├── model_config.py       # ✅ 模型配置
├── chat.py              # ✅ 聊天请求
├── conversation.py      # 📋 待迁移
├── message.py           # 📋 待迁移
├── user.py             # 📋 待检查
├── auth.py             # 📋 待创建
├── file.py             # 📋 待创建
└── llm_config.py        # ✅ 兼容层（已废弃）
```

---

## 验证完成

所有模块重构完成后，应该满足：

- [ ] 每个模块有独立的 schema 文件
- [ ] 所有 schema 遵循 Base/Create/Update/InDB/Response 模式
- [ ] 没有混合多个模块的 schema 文件
- [ ] API 端点使用正确的 schema 类型
- [ ] 有辅助函数处理转换逻辑
- [ ] 所有测试通过
- [ ] API 文档正确生成

