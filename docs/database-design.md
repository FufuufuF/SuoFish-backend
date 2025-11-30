# ChatBot Database Design

## 概述

ChatBot 是一个基于 LLM 的对话系统，支持用户进行多轮对话。本文档描述了系统的数据库设计方案。

## 实体关系图

```
User (1) ────── (N) Conversation (1) ────── (N) Message
```

- **User**: 用户表，存储用户信息
- **Conversation**: 会话表，存储用户创建的对话会话
- **Message**: 消息表，存储会话中的消息（用户消息和 AI 回复）

## 表结构设计

### 1. User 表

存储用户信息，用于身份验证和会话管理。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 用户主键ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱地址 |
| password | VARCHAR(255) | NOT NULL | 加密后的密码 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引：**
- idx_username (username)
- idx_email (email)

### 2. Conversation 表

存储用户创建的对话会话，每个会话包含多条消息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 会话主键ID |
| user_id | INT | FOREIGN KEY → user(id), NOT NULL | 所属用户ID |
| name | VARCHAR(100) | DEFAULT 'New Chat' | 会话名称 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP | 最后更新时间 |

**索引：**
- idx_user_id (user_id)

**外键约束：**
- user_id → user(id) ON DELETE CASCADE

### 3. Message 表

存储会话中的所有消息，包括用户输入和 AI 回复。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 消息主键ID |
| conversation_id | INT | FOREIGN KEY → conversation(id), NOT NULL | 所属会话ID |
| role | VARCHAR(20) | NOT NULL | 消息角色 ('user' 或 'assistant') |
| content | TEXT | NOT NULL | 消息内容 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引：**
- idx_conversation_id (conversation_id)

**外键约束：**
- conversation_id → conversation(id) ON DELETE CASCADE

## 数据流说明

### 1. 新用户注册
```
用户提交注册信息 → 创建 User 记录 → 返回用户ID
```

### 2. 创建新会话
```
用户登录 → 创建 Conversation 记录 → 返回会话ID
```

### 3. 发送消息并获取回复
```
用户发送消息 → 创建用户Message记录 → 调用LLM → 创建AI Message记录 → 返回消息流
```

### 4. 会话列表查询
```
用户ID → 查询Conversation列表 → 按updated_at倒序排序
```

### 5. 会话详情查询
```
会话ID → 查询Message列表 → 按created_at正序排序
```

## 设计考虑

### 时间戳策略
- `created_at`: 记录创建时间，用于消息排序和会话排序
- `updated_at`: 记录最后修改时间，用于会话排序（最近对话在前）

### 外键约束
- 使用 CASCADE 删除：删除用户时自动删除所有相关会话和消息
- 使用 CASCADE 删除：删除会话时自动删除所有相关消息

### 索引策略
- 主键自动创建索引
- 外键字段创建索引，提升查询性能
- 常用查询字段（如 username, email）创建索引

### 数据类型选择
- 使用 TEXT 存储消息内容，支持长文本
- 使用 VARCHAR(255) 存储邮箱，符合标准长度
- 使用 VARCHAR(50) 存储用户名，限制长度避免滥用

