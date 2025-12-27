# Backend Project Documentation

该项目是一个基于 FastAPI 的后端服务，集成了 LangChain 和 RAG（检索增强生成）功能，支持多轮对话、知识库管理和文件处理。

## 📁 目录结构

主要目录结构说明：

- `src/api`: API 路由定义 (v1)
- `src/core`: 核心配置 (Config)
- `src/db`: 数据库模型 (Models) 和会话管理 (Session)
- `src/services`: 业务逻辑层 (Chat, RAG, Knowledge Base)
- `src/schemas`: Pydantic 数据模型 schemas
- `src/utils`: 工具函数

## 🚀 如何运行

### 1. 环境准备

确保已安装 Python 3.11+ 和 `uv` (推荐) 或 `pip`.

### 2. 安装依赖

如果使用的是 `uv` (正如项目配置所示):

```bash
uv sync
```

或者使用 pip:

```bash
pip install -r requirements.txt  # 如果生成了 requirements.txt
# 或者直接根据 pyproject.toml 安装
pip install .
```

### 3. 配置环境变量

复制 `.env_example` 为 `.env` 并配置必要的环境变量（如数据库连接、OpenAI API Key 等）。

```bash
cp .env_example .env
```

### 4. 启动服务

使用 Uvicorn 启动开发服务器：

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，API 文档可访问：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## ✨ 支持功能

### 1. 认证与用户管理 (`/auth`, `/user`)

- 用户注册与登录
- JWT Token 认证
- 用户信息管理
- 默认模型配置管理

### 2. 智能对话 (`/chat`)

- **流式响应**: 支持 Server-Sent Events (SSE) / NDJSON 格式的流式对话。
- **多模态支持**: 支持上传文件（PDF, DOCX, PPTX）并在对话中引用。
- **RAG 集成**: 支持关联知识库，模型可基于知识库内容回答问题。
- **上下文记忆**: 自动维护会话历史。

### 3. 知识库管理 (`/knowledge-base`)

- **创建与管理**: 用户可创建多个知识库。
- **文件处理**:
  - 支持上传文档至知识库。
  - 后台异步处理：文档自动进行切片 (Chunking) 和 向量化 (Embedding)。
  - 状态追踪：上传 -> 切片中 -> 已发布。
- **向量检索**: 基于 ChromaDB (推测) 或其他向量库进行语义检索。

### 4. 会话与消息 (`/conversations`, `/messages`)

- 历史会话管理（创建、删除、重命名）。
- 历史消息查询。

## 🔧 配置指南

本项目推荐将 AI 模型配置（如 API Key）存储在数据库中，以便在前端动态管理。

1.  **数据库配置 (推荐)**：

    - 系统启动后，用户可在前端界面添加"模型配置"。
    - 配置信息安全地存储在 MySQL 数据库 (`model_config` 表) 中。
    - 调用 `/chat` 接口时，系统会优先使用用户的默认模型配置。

2.  **环境变量配置 (兜底)**：
    - 如果数据库中未找到配置，系统会尝试读取环境变量 (`.env`) 作为兜底。
    - 修改 `.env` 文件可设置默认的全局 API Key (见 `.env_example`)。

## 🗄️ 数据库设计

本项目采用 **关系型数据库 (MySQL)** 和 **向量数据库 (ChromaDB)** 混合存储方案。

### 1. MySQL (关系型数据)

用于存储用户、会话、消息记录及业务配置。

#### 基本信息

- **User (用户表)**

  - `id`: `Integer` (PK)
  - `username`: `String` (Unique)
  - `email`: `String` (Unique)
  - `password`: `String` (Hashed)
  - `default_model_config_id`: `Integer` (FK -> ModelConfig) - 用户当前的默认模型
  - `created_at`: `DateTime`

- **ModelConfig (模型配置表)**
  - `id`: `Integer` (PK)
  - `user_id`: `Integer` (FK -> User)
  - `model_name`: `String` (e.g., "qwen-plus")
  - `api_key`: `String`
  - `base_url`: `String`
  - `temperature`: `Float`
  - `max_tokens`: `Integer`

#### 对话系统

- **Conversation (会话表)**

  - `id`: `Integer` (PK)
  - `user_id`: `Integer` (FK -> User)
  - `name`: `String` - 会话标题
  - `summary`: `Text` - 自动生成的长会话摘要
  - `created_at`, `updated_at`: `DateTime`

- **Message (消息表)**

  - `id`: `Integer` (PK)
  - `conversation_id`: `Integer` (FK -> Conversation)
  - `role`: `String` ('user' | 'assistant')
  - `content`: `Text` - 消息内容

- **ConversationFile (会话文件表)**
  - `id`: `Integer` (PK)
  - `conversation_id`: `Integer` (FK -> Conversation)
  - `user_id`: `Integer` (FK -> User)
  - `file_name`: `String` - 原始文件名
  - `file_type`: `String` - 文件类型 (docx/pptx/etc)
  - `storage_path`: `String` - 本地存储路径
  - `status`: `String` - 状态 (uploaded/processing/etc)

#### 知识库系统

- **KnowledgeBase (知识库表)**

  - `id`: `Integer` (PK)
  - `status`: `Integer` (0: Uploading, 1: Chunking, 2: Published)
  - `file_list`: `JSON` - 文件元数据快照

- **KnowledgeBaseFile (知识库文件表)**
  - `id`: `Integer` (PK)
  - `knowledge_base_id`: `Integer` (FK -> KnowledgeBase)
  - `file_name`: `String`
  - `file_path`: `String`
  - `file_size`: `Integer`
  - `file_type`: `String`
  - `file_content`: `Text` - 提取的文本内容（可选）

#### 日志系统

- **ConversationLogSession (会话日志会话)**

  - `id`: `Integer` (PK)
  - `conversation_id`: `Integer` (FK -> Conversation)
  - `user_id`: `Integer` (FK -> User)
  - `total_rounds`: `Integer`
  - `has_errors`: `Boolean`

- **ConversationLogRound (会话日志回合)**
  - `id`: `Integer` (PK)
  - `session_id`: `Integer` (FK -> ConversationLogSession)
  - `round_number`: `Integer`
  - `user_message`: `Text`
  - `assistant_message`: `Text`
  - `files_result`: `JSON` - 文件处理结果快照
  - `rag_results`: `JSON` - RAG 检索结果快照
  - `error`: `Text` - 运行时错误信息

### 2. ChromaDB (向量数据)

用于存储文档的 Embedding 向量，支持 RAG 语义检索。

- **Storage**: 本地文件系统 (`./chroma_data`) 或 独立服务模式。
- **Collection**: `documents` (默认集合名)
- **Metadata**:
  - `file_id`: 关联到 MySQL 中的文件记录
  - `user_id`: 数据隔离
  - `knowledge_base_id`: 归属知识库
  - `source_type`: 来源类型 ('knowledge_base' | 'conversation')

## 📝 其他说明

- **并发模型**: 全程使用 `async/await` 异步编程模型，提升 I/O 密集型任务（数据库、LLM API 调用）的性能。
- **API 规范**: 遵循 RESTful 风格，统一使用 `APIResponse` 结构返回数据。
