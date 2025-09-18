# 问客AI平台 API 文档

## 概述
问客AI平台是一个基于FastAPI构建的智能对话平台，提供用户管理、商户管理、智能体管理、聊天会话等功能。

**基础信息**
- 基础URL: `http://localhost:8000/api/v1`
- 认证方式: Bearer Token (JWT)
- 默认用户: admin/admin123

## 认证接口

### 1. 用户登录
**端点**: `POST /auth/login`

**请求示例**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. 获取当前用户信息
**端点**: `GET /auth/me`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "merchant_id": 859534,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### 3. 验证令牌
**端点**: `GET /auth/verify`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**: HTTP 200 OK (验证成功)

## 用户管理接口

### 1. 获取用户列表
**端点**: `GET /users/`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "merchant_id": 859534,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "username": "user1",
    "email": "user1@example.com",
    "merchant_id": 859534,
    "is_active": true,
    "created_at": "2024-01-02T00:00:00"
  }
]
```

### 2. 创建用户
**端点**: `POST /users/`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "merchant_id": 859534
}
```

**响应示例**:
```json
{
  "id": 3,
  "username": "newuser",
  "email": "newuser@example.com",
  "merchant_id": 859534,
  "is_active": true,
  "created_at": "2024-01-03T00:00:00"
}
```

## 商户管理接口

### 1. 获取商户列表
**端点**: `GET /merchants/`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  {
    "id": 859534,
    "name": "测试商户",
    "description": "测试商户描述",
    "status": "active",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### 2. 创建商户
**端点**: `POST /merchants/`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "name": "新商户",
  "description": "新商户的描述信息",
  "status": "active"
}
```

**响应示例**:
```json
{
  "id": 859535,
  "name": "新商户",
  "description": "新商户的描述信息",
  "status": "active",
  "created_at": "2024-01-02T00:00:00"
}
```

## 智能体管理接口

### 1. 获取智能体列表
**端点**: `GET /agents/`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "dify测试",
    "description": "Dify平台测试智能体",
    "model": "gpt-3.5-turbo",
    "status": "active",
    "merchant_id": 859534,
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "name": "晧客数据",
    "description": "皓客数据智能体",
    "model": "gpt-4",
    "status": "active",
    "merchant_id": 859534,
    "created_at": "2024-01-02T00:00:00"
  }
]
```

### 2. 创建智能体
**端点**: `POST /agents/`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "name": "客服助手",
  "description": "客户服务智能助手",
  "model": "gpt-3.5-turbo",
  "status": "active",
  "merchant_id": 859534
}
```

**响应示例**:
```json
{
  "id": 3,
  "name": "客服助手",
  "description": "客户服务智能助手",
  "model": "gpt-3.5-turbo",
  "status": "active",
  "merchant_id": 859534,
  "created_at": "2024-01-03T00:00:00"
}
```

## 聊天功能接口

### 1. 非流式聊天
**端点**: `POST /chat/completions`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "query": "你好，请介绍一下你自己",
  "user_id": "1",
  "merchant_id": 859534,
  "agent_id": 1,
  "stream": false
}
```

**响应示例**:
```json
{
  "message": "你好！我是问客AI平台的智能助手，我可以帮助您处理各种问题和任务...",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 45,
    "total_tokens": 65
  }
}
```

### 2. 流式聊天
**端点**: `POST /chat/completions/stream`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "query": "你好，请介绍一下你自己",
  "user_id": "1",
  "merchant_id": 859534,
  "agent_id": 1,
  "stream": true
}
```

**响应格式** (Server-Sent Events):
```
data: {"message": "你好", "chunk": 1}

data: {"message": "！我是", "chunk": 2}

data: {"message": "问客AI", "chunk": 3}

data: [DONE]
```

## 会话管理接口

### 1. 获取会话列表
**端点**: `GET /sessions/`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  {
    "id": "00668ff5-c0c7-46f4-9be8-cf5f9051bf5c",
    "title": "Chat with 晧客数据",
    "user_id": 1,
    "merchant_id": 859534,
    "agent_id": 2,
    "status": "active",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

### 2. 创建会话
**端点**: `POST /sessions/`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "title": "测试会话",
  "user_id": "1",
  "merchant_id": 859534,
  "agent_id": 1,
  "status": "active"
}
```

**响应示例**:
```json
{
  "id": "864e7ea0-9a41-46c7-b074-777db494e482",
  "title": "测试会话",
  "user_id": 1,
  "merchant_id": 859534,
  "agent_id": 1,
  "status": "active",
  "created_at": "2024-01-02T12:00:00"
}
```

### 3. 获取会话详情
**端点**: `GET /sessions/{session_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "id": "864e7ea0-9a41-46c7-b074-777db494e482",
  "title": "测试会话",
  "user_id": 1,
  "merchant_id": 859534,
  "agent_id": 1,
  "status": "active",
  "created_at": "2024-01-02T12:00:00",
  "updated_at": "2024-01-02T12:30:00"
}
```

## 消息管理接口

### 1. 获取消息列表
**端点**: `GET /messages/`

**查询参数**:
- `session_id` (可选): 过滤特定会话的消息

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  {
    "id": 4725,
    "content": "这是一条测试消息",
    "role": "user",
    "conversation_id": "864e7ea0-9a41-46c7-b074-777db494e482",
    "user_id": 1,
    "merchant_id": 859534,
    "agent_id": 1,
    "created_at": "2024-01-02T12:05:00"
  }
]
```

### 2. 创建消息
**端点**: `POST /messages/`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求示例**:
```json
{
  "content": "这是一条测试消息",
  "role": "user",
  "conversation_id": "864e7ea0-9a41-46c7-b074-777db494e482",
  "user_id": "1",
  "merchant_id": 859534,
  "agent_id": 1
}
```

**响应示例**:
```json
{
  "id": 4726,
  "content": "这是一条测试消息",
  "role": "user",
  "conversation_id": "864e7ea0-9a41-46c7-b074-777db494e482",
  "user_id": 1,
  "merchant_id": 859534,
  "agent_id": 1,
  "created_at": "2024-01-02T12:10:00"
}
```

## 健康检查接口

### 1. 健康检查
**端点**: `GET /`

**响应示例**:
```json
{
  "message": "欢迎使用问客AI平台API"
}
```

## 错误响应

### 通用错误格式
```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码
- `401 Unauthorized`: 认证失败或Token无效
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求参数验证失败
- `500 Internal Server Error`: 服务器内部错误

## Python客户端示例

### 基本使用
```python
import requests
import json

# API配置
BASE_URL = "http://localhost:8000/api/v1"

# 登录获取Token
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = response.json()["access_token"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 获取用户信息
user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(user_response.json())

# 发送聊天消息
chat_data = {
    "query": "你好，请介绍一下你自己",
    "user_id": "1",
    "merchant_id": 859534,
    "agent_id": 1,
    "stream": false
}

chat_response = requests.post(
    f"{BASE_URL}/chat/completions", 
    json=chat_data, 
    headers=headers
)
print(chat_response.json())
```

## 测试脚本
项目包含完整的API测试脚本：`test/comprehensive_api_test.py`

运行测试：
```bash
python test/comprehensive_api_test.py
```

## 环境要求
- Python 3.8+
- 依赖包: 参见 `requirements.txt`
- 数据库: MySQL

## 启动服务
```bash
# 开发模式（热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python main.py
```