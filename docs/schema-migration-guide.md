# Schema 重构迁移指南

## 🎯 快速导入更新手册

如果你的代码中使用了旧的导入，请按照此指南更新：

## 📦 导入更新对照表

### 1. 认证相关（auth）

#### ❌ 旧的导入
```python
from src.schemas.sign import SignUp, SignIn
```

#### ✅ 新的导入
```python
from src.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
```

#### 重命名对照
| 旧名称 | 新名称 | 用途 |
|--------|--------|------|
| `SignUp` | `UserRegister` | 用户注册请求 |
| `SignIn` | `UserLogin` | 用户登录请求 |
| - | `UserResponse` | 用户信息响应（新增） |
| - | `TokenResponse` | Token 响应（新增） |

---

### 2. 模型配置（model_config）

#### ❌ 旧的导入
```python
from src.schemas.llm_config import ModelConfigCreate, ModelConfigResponse
```

#### ✅ 新的导入
```python
from src.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
    ModelConfigListResponse,
)
```

#### 新增 Schema
- `ModelConfigBase` - 基础字段
- `ModelConfigUpdate` - 更新请求（所有字段 Optional）
- `ModelConfigInDB` - 数据库完整数据
- `ModelConfigListResponse` - 列表响应

---

### 3. 聊天元数据（ChatMetadata）

#### ❌ 旧的导入
```python
from src.schemas.llm_config import ChatMetadata
```

#### ✅ 新的导入
```python
from src.schemas.chat import ChatMetadata
```

---

### 4. 会话相关（conversation）

#### ❌ 旧的导入
```python
from src.schemas.chat import ConversationResponse
```

#### ✅ 新的导入
```python
from src.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
)
```

---

### 5. 消息相关（message）

#### ❌ 旧的导入
```python
from src.schemas.chat import MessageResponse
```

#### ✅ 新的导入
```python
from src.schemas.message import (
    MessageRole,          # 枚举类型
    MessageCreate,
    MessageResponse,
    MessageListResponse,
)
```

---

### 6. 聊天请求（chat）

#### ✅ 保持不变（但有新增）
```python
from src.schemas.chat import (
    ChatRequest,      # 原 Chat
    ChatResponse,     # 新增
    ChatMetadata,     # 保留
    StreamChunk,      # 新增（流式响应）
)
```

#### 别名支持
- `Chat` → `ChatRequest`（向后兼容别名）

---

## 🔧 代码更新示例

### 示例 1: 认证端点

#### ❌ 旧代码
```python
from src.schemas.sign import SignUp, SignIn

@router.post("/signup")
async def sign_up(sign_up: SignUp, db: AsyncSession = Depends(get_db)):
    user = User(**sign_up.model_dump())
    ...
```

#### ✅ 新代码
```python
from src.schemas.auth import UserRegister, UserLogin

@router.post("/signup")
async def sign_up(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = User(**user_data.model_dump())
    ...
```

---

### 示例 2: 会话列表

#### ❌ 旧代码
```python
from src.schemas.chat import ConversationResponse

@router.get("/")
async def get_conversations(db: AsyncSession = Depends(get_db)):
    conversations = await get_all_conversations(db)
    data = [ConversationResponse.model_validate(c) for c in conversations]
    return {"conversations": data}
```

#### ✅ 新代码
```python
from src.schemas.conversation import ConversationResponse, ConversationListResponse

@router.get("/")
async def get_conversations(db: AsyncSession = Depends(get_db)):
    conversations = await get_all_conversations(db)
    data = [ConversationResponse.model_validate(c) for c in conversations]
    
    # 使用专门的列表响应 Schema
    response = ConversationListResponse(
        conversations=data,
        total=len(data)
    )
    return response
```

---

### 示例 3: 消息角色

#### ❌ 旧代码
```python
# 使用字符串
message = Message(role="user", content="Hello")
```

#### ✅ 新代码
```python
from src.schemas.message import MessageRole

# 使用枚举，类型更安全
message = Message(role=MessageRole.USER, content="Hello")

# 或者仍然可以使用字符串（Pydantic 会自动转换）
message = Message(role="user", content="Hello")
```

---

## 📋 批量更新脚本

如果你有很多文件需要更新，可以使用以下命令：

```bash
# 1. 更新认证相关导入
find src -name "*.py" -type f -exec sed -i '' \
  's/from src\.schemas\.sign import/from src.schemas.auth import/g' {} +

# 2. 更新模型配置导入
find src -name "*.py" -type f -exec sed -i '' \
  's/from src\.schemas\.llm_config import ModelConfig/from src.schemas.model_config import ModelConfig/g' {} +

# 3. 更新会话导入
find src -name "*.py" -type f -exec sed -i '' \
  's/from src\.schemas\.chat import ConversationResponse/from src.schemas.conversation import ConversationResponse/g' {} +

# 4. 更新消息导入
find src -name "*.py" -type f -exec sed -i '' \
  's/from src\.schemas\.chat import MessageResponse/from src.schemas.message import MessageResponse/g' {} +

# 5. 更新 ChatMetadata 导入
find src -name "*.py" -exec sed -i '' \
  's/from src\.schemas\.llm_config import ChatMetadata/from src.schemas.chat import ChatMetadata/g' {} +
```

**注意**：macOS 使用 `sed -i ''`，Linux 使用 `sed -i`

---

## ✅ 验证步骤

更新导入后，按照以下步骤验证：

### 1. 语法检查
```bash
python -m py_compile $(find src -name "*.py" -type f)
```

### 2. 导入检查
```bash
python -c "
from src.schemas.auth import UserRegister, UserLogin
from src.schemas.model_config import ModelConfigCreate
from src.schemas.conversation import ConversationResponse
from src.schemas.message import MessageResponse
from src.schemas.chat import ChatMetadata
print('✅ All imports successful')
"
```

### 3. 启动服务器
```bash
uvicorn main:app --reload
```

检查是否有导入错误。

### 4. 测试 API
```bash
# 测试认证端点
curl http://localhost:8000/api/v1/auth/

# 测试模型配置
curl http://localhost:8000/api/v1/model/get

# 测试会话列表
curl http://localhost:8000/api/v1/conversations/
```

---

## 🐛 常见问题

### Q1: ImportError: cannot import name 'SignUp'
**原因**：`sign.py` 已删除
**解决**：更新导入为 `from src.schemas.auth import UserRegister`

### Q2: ImportError: cannot import name 'ModelConfigCreate' from 'src.schemas.llm_config'
**原因**：`llm_config.py` 已删除
**解决**：更新导入为 `from src.schemas.model_config import ModelConfigCreate`

### Q3: ImportError: cannot import name 'ConversationResponse' from 'src.schemas.chat'
**原因**：`ConversationResponse` 已迁移到 `conversation.py`
**解决**：更新导入为 `from src.schemas.conversation import ConversationResponse`

### Q4: 服务器启动时报错 email-validator 未安装
**原因**：之前使用了 `EmailStr` 类型
**解决**：已修复，现在使用自定义邮箱验证器

---

## 📚 更多资源

- 详细设计指南：`docs/schema-design-guide.md`
- 快速参考：`docs/schema-quick-reference.md`
- 重构总结：`docs/schema-refactor-summary.md`

---

## 🎉 完成

按照此指南更新导入后，你的代码将：
- ✅ 使用最新的 schema 结构
- ✅ 遵循最佳实践
- ✅ 类型更安全
- ✅ 更易维护

如有问题，请查看相关文档或检查服务器日志。

