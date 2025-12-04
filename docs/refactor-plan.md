# 项目结构重构技术文档

## 1. 重构目标

- **解耦**：AI 能力层与业务服务层分离
- **可扩展**：为 RAG、Agent 等功能预留位置
- **可读性**：目录结构清晰，职责明确
- **最佳实践**：配置管理使用 Pydantic Settings

---

## 2. 目录结构对比

### 2.1 当前结构

```
src/
├── api/
│   └── v1/
│       └── endpoints/
├── core/
│   └── config.py              # 所有配置混在一起
├── crud/
├── db/
│   └── models/
├── llm/
│   └── llm_service.py         # LLM 服务
├── schemas/
├── services/
│   ├── chat_service.py
│   └── file_service.py
└── utils/
    ├── authentic.py
    └── micorsoft_office_reader.py  # 文件解析器
```

### 2.2 重构后结构

```
src/
├── ai/                                 # 🤖 AI 核心能力层
│   ├── __init__.py
│   │
│   ├── llm/                            # 大模型服务
│   │   ├── __init__.py
│   │   ├── base.py                     # LLM 抽象基类
│   │   └── chat_model.py               # 聊天模型实现（原 llm_service.py）
│   │
│   ├── embedding/                      # 向量嵌入服务（预留）
│   │   ├── __init__.py
│   │   └── base.py                     # Embedding 抽象基类
│   │
│   ├── rag/                            # RAG 相关
│   │   ├── __init__.py
│   │   ├── document_parser.py          # 文档解析（原 micorsoft_office_reader.py）
│   │   ├── chunking.py                 # 文档分块（预留）
│   │   ├── retriever.py                # 检索器（预留）
│   │   └── vector_store.py             # 向量存储（预留）
│   │
│   └── agent/                          # Agent 智能体（预留）
│       ├── __init__.py
│       └── base.py
│
├── services/                           # 📦 业务服务层
│   ├── __init__.py
│   ├── chat_service.py                 # 顶级聊天服务（编排 AI + 业务）
│   ├── file_service.py                 # 文件上传/存储服务
│   └── rag_service.py                  # RAG 编排服务（预留）
│
├── api/                                # 🌐 API 接口层
│   ├── __init__.py
│   ├── deps.py                         # FastAPI 依赖项
│   └── v1/
│       ├── api.py
│       └── endpoints/
│           ├── auth.py
│           ├── chat.py
│           ├── conversations.py
│           └── messages.py
│
├── core/                               # ⚙️ 核心配置
│   ├── __init__.py
│   └── config/
│       ├── __init__.py                 # 导出所有配置
│       ├── settings.py                 # 基础设置 + 环境加载
│       ├── database.py                 # 数据库配置
│       ├── auth.py                     # JWT/认证配置
│       └── ai.py                       # AI 相关配置（LLM、Embedding）
│
├── crud/                               # 💾 数据访问层
│   ├── __init__.py
│   ├── user.py
│   ├── conversation.py
│   ├── message.py
│   └── conversation_file.py
│
├── db/                                 # 🗄️ 数据库
│   ├── __init__.py
│   ├── session.py
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       ├── conversation.py
│       ├── message.py
│       └── conversation_file.py
│
├── schemas/                            # 📋 Pydantic 数据模型
│   ├── __init__.py
│   ├── api_response.py
│   ├── chat.py
│   ├── llm_config.py
│   └── sign.py
│
└── utils/                              # 🔧 通用工具
    ├── __init__.py
    └── authentic.py                    # JWT 工具函数
```

---

## 3. 分层架构说明

```
┌─────────────────────────────────────────────────────────────┐
│                        API 层 (api/)                        │
│              处理 HTTP 请求/响应，参数校验                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   业务服务层 (services/)                     │
│           编排 AI 能力 + 业务逻辑 + 调用 CRUD                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ChatService  │  │FileService  │  │RagService   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌───────────┐ ┌───────────────┐
│  AI 能力层      │ │ CRUD 层   │ │  工具层       │
│  (ai/)          │ │ (crud/)   │ │  (utils/)     │
│                 │ │           │ │               │
│ ┌─────────────┐ │ │ 数据库    │ │ 通用工具函数  │
│ │ llm/        │ │ │ 操作      │ │               │
│ ├─────────────┤ │ └───────────┘ └───────────────┘
│ │ embedding/  │ │
│ ├─────────────┤ │
│ │ rag/        │ │
│ ├─────────────┤ │
│ │ agent/      │ │
│ └─────────────┘ │
└─────────────────┘
```

### 各层职责

| 层级 | 目录 | 职责 | 可以依赖 |
|------|------|------|----------|
| API 层 | `api/` | HTTP 处理、参数校验、响应格式化 | services, schemas |
| 业务服务层 | `services/` | 业务逻辑编排、事务管理 | ai, crud, schemas |
| AI 能力层 | `ai/` | 纯 AI 能力封装，无业务逻辑 | core/config, 外部 API |
| 数据访问层 | `crud/` | 数据库 CRUD 操作 | db/models |
| 工具层 | `utils/` | 通用工具函数 | 无（最底层） |

---

## 4. 配置管理重构

### 4.1 使用 Pydantic Settings（最佳实践）

**`src/core/config/settings.py`**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用基础配置"""
    app_name: str = "ChatBot"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """缓存配置实例，避免重复读取"""
    return Settings()
```

**`src/core/config/database.py`**

```python
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    host: str
    port: int = 3306
    name: str
    user: str
    password: str
    
    class Config:
        env_prefix = "DB_"  # 环境变量前缀：DB_HOST, DB_PORT...
    
    @property
    def async_url(self) -> str:
        """异步数据库连接 URL"""
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        """同步数据库连接 URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
```

**`src/core/config/auth.py`**

```python
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    """认证配置"""
    secret_key: str
    algorithm: str = "HS256"
    expiration_time: int = 3600  # 秒
    
    class Config:
        env_prefix = "JWT_"
```

**`src/core/config/ai.py`**

```python
from pydantic_settings import BaseSettings
from typing import Optional


class LLMSettings(BaseSettings):
    """LLM 配置"""
    api_key: str
    base_url: str
    model_name: str = "qwen-plus"
    
    class Config:
        env_prefix = "QWEN_"


class EmbeddingSettings(BaseSettings):
    """Embedding 配置（预留）"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str = "text-embedding-v1"
    
    class Config:
        env_prefix = "EMBEDDING_"


class AISettings(BaseSettings):
    """AI 总配置"""
    llm: LLMSettings = LLMSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
```

**`src/core/config/__init__.py`**

```python
from functools import lru_cache
from .database import DatabaseSettings
from .auth import AuthSettings
from .ai import LLMSettings, EmbeddingSettings

# 导出配置实例（带缓存）
@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()

@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()

@lru_cache
def get_llm_settings() -> LLMSettings:
    return LLMSettings()

# 便捷导出
database = get_database_settings()
auth = get_auth_settings()
llm = get_llm_settings()
```

### 4.2 环境变量命名规范

```bash
# .env 文件

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=chatbot
DB_USER=root
DB_PASSWORD=password

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME=3600

# LLM
QWEN_API_KEY=your-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_NAME=qwen-plus

# Embedding（预留）
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=
EMBEDDING_MODEL_NAME=text-embedding-v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 5. AI 模块设计

### 5.1 LLM 模块

**`src/ai/llm/base.py`** - 抽象基类（便于未来切换模型）

```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List


class BaseLLM(ABC):
    """LLM 抽象基类"""
    
    @abstractmethod
    async def generate(self, messages: List[dict]) -> str:
        """非流式生成"""
        pass
    
    @abstractmethod
    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        """流式生成"""
        pass
```

**`src/ai/llm/chat_model.py`** - 具体实现

```python
from typing import AsyncGenerator, List, Optional
from langchain_openai import ChatOpenAI

from src.core.config import llm as llm_config
from .base import BaseLLM


class ChatModel(BaseLLM):
    """聊天模型实现"""
    
    def __init__(self):
        self.client = ChatOpenAI(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            model=llm_config.model_name,
        )
    
    async def generate(self, messages: List[dict]) -> str:
        response = await self.client.ainvoke(messages)
        return response.content
    
    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        async for chunk in self.client.astream(messages):
            if chunk.content:
                yield chunk.content
```

### 5.2 RAG 模块

**`src/ai/rag/document_parser.py`** - 文档解析（原 micorsoft_office_reader.py）

```python
from io import BytesIO
from typing import Union
# ... 保持原有实现，重命名类为 DocumentParser
```

**`src/ai/rag/chunking.py`** - 文档分块（预留）

```python
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class Chunk:
    """文档分块"""
    content: str
    metadata: dict  # 来源文件、页码等


class BaseChunker(ABC):
    """分块器抽象基类"""
    
    @abstractmethod
    def split(self, text: str) -> List[Chunk]:
        pass


class RecursiveChunker(BaseChunker):
    """递归分块器（预留实现）"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str) -> List[Chunk]:
        # TODO: 实现
        pass
```

---

## 6. 迁移步骤

### 第一阶段：创建目录结构

```bash
# 1. 创建 AI 模块目录
mkdir -p src/ai/{llm,embedding,rag,agent}
touch src/ai/__init__.py
touch src/ai/llm/{__init__.py,base.py,chat_model.py}
touch src/ai/embedding/{__init__.py,base.py}
touch src/ai/rag/{__init__.py,document_parser.py,chunking.py,retriever.py,vector_store.py}
touch src/ai/agent/{__init__.py,base.py}

# 2. 创建配置目录
mkdir -p src/core/config
touch src/core/config/{__init__.py,settings.py,database.py,auth.py,ai.py}
```

### 第二阶段：迁移文件

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `src/llm/llm_service.py` | `src/ai/llm/chat_model.py` | 重命名 + 重构 |
| `src/utils/micorsoft_office_reader.py` | `src/ai/rag/document_parser.py` | 移动 + 重命名 |
| `src/core/config.py` | `src/core/config/*.py` | 拆分为多个文件 |

### 第三阶段：更新导入路径

需要更新以下文件的 import 语句：
- `src/services/chat_service.py`
- `src/services/file_service.py`
- `src/db/session.py`
- `src/api/v1/endpoints/*.py`
- `src/utils/authentic.py`

### 第四阶段：添加依赖

```bash
# 添加 pydantic-settings
uv add pydantic-settings
```

---

## 7. 预留模块说明

以下模块暂时只创建空文件和基类，后续按需实现：

| 模块 | 文件 | 用途 |
|------|------|------|
| Embedding | `src/ai/embedding/base.py` | 文本向量化 |
| Chunking | `src/ai/rag/chunking.py` | 文档分块 |
| Vector Store | `src/ai/rag/vector_store.py` | 向量存储 |
| Retriever | `src/ai/rag/retriever.py` | 相似度检索 |
| Agent | `src/ai/agent/base.py` | 智能体框架 |
| RAG Service | `src/services/rag_service.py` | RAG 流程编排 |

---

## 8. 总结

本次重构主要完成：

1. ✅ 将 AI 相关能力统一到 `src/ai/` 目录
2. ✅ 配置管理改用 Pydantic Settings，按功能拆分
3. ✅ 为 RAG、Agent 等功能预留目录结构
4. ✅ 保持分层架构，各层职责明确

重构后的代码将更易于：
- 添加新的 AI 能力（Embedding、Agent 等）
- 切换不同的 LLM/Embedding 模型
- 单元测试（各层可独立 mock）
- 团队协作（目录职责清晰）

