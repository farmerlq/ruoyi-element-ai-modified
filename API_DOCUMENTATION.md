# 问客项目 - 前后端API接口文档

## 1. 概述

本文档详细描述了问客项目的前后端API接口规范，包括认证、聊天、智能体、会话和消息管理等功能模块。

## 2. 基础信息

- **API Base URL**: `http://localhost:8000/api` (开发环境)
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **响应状态码**: 遵循HTTP标准状态码

## 3. 认证接口 (Authentication)

### 3.1 用户登录

**接口**: `POST /api/auth/login`

**描述**: 用户登录并获取访问令牌

**请求参数**: 
```json
{
  "username": "string",
  "password": "string"
}
```

**响应参数**: 
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "userInfo": {
    "user_id": "number",
    "username": "string",
    "email": "string",
    "merchant_id": "number",
    "role": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  }
}
```

**状态码**: 
- `200`: 登录成功
- `401`: 用户名或密码错误

### 3.2 获取当前用户信息

**接口**: `GET /api/auth/me`

**描述**: 获取当前登录用户的详细信息

**请求头**: 
- `Authorization: Bearer {token}`

**响应参数**: 
```json
{
  "id": "number",
  "username": "string",
  "email": "string",
  "merchant_id": "number",
  "role": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `200`: 获取成功
- `401`: 未授权

### 3.3 验证令牌

**接口**: `GET /api/auth/verify`

**描述**: 验证JWT令牌的有效性

**请求头**: 
- `Authorization: Bearer {token}`

**响应参数**: 
```json
{
  "sub": "string",
  "merchant_id": "number",
  "user_id": "number",
  "role": "string",
  "exp": "number"
}
```

**状态码**: 
- `200`: 令牌有效
- `401`: 令牌无效

## 4. 聊天接口 (Chat)

### 4.1 聊天完成接口

**接口**: `POST /api/chat/completions`

**描述**: 向智能体发送消息并获取响应（支持流式和非流式）

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
```json
{
  "query": "string",
  "user_id": "number",
  "merchant_id": "number",
  "agent_id": "number",
  "conversation_id": "string" (可选)
}
```

**响应参数**: 

#### 4.1.1 流式响应 (Content-Type: text/event-stream)

```
// 消息内容事件
data: {"event":"message","answer":"回复内容"}

// 统计信息事件
data: {"event":"statistics","event_count":10,"total_tokens":123,"estimated_cost":0.0015}

// 结束标记
data: [DONE]
```

#### 4.1.2 非流式响应 (Content-Type: application/json)

```json
{
  "message": "string",
  "message_id": "string",
  "total_tokens_estimated": "number",
  "estimated_cost": "number"
}
```

**状态码**: 
- `200`: 请求成功
- `401`: 未授权
- `404`: 智能体不存在
- `500`: 服务器错误

## 5. 智能体接口 (Agents)

### 5.1 创建智能体

**接口**: `POST /api/agents/`

**描述**: 创建新的智能体

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
```json
{
  "name": "string",
  "description": "string",
  "config": {"key": "value"}, // 或字符串格式
  "merchant_id": "number",
  "status": "string"
}
```

**响应参数**: 
```json
{
  "id": "number",
  "name": "string",
  "description": "string",
  "config": {"key": "value"},
  "merchant_id": "number",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `201`: 创建成功
- `403`: 无权限

### 5.2 获取智能体详情

**接口**: `GET /api/agents/{agent_id}`

**描述**: 获取指定智能体的详细信息

**请求头**: 
- `Authorization: Bearer {token}`

**响应参数**: 
```json
{
  "id": "number",
  "name": "string",
  "description": "string",
  "config": {"key": "value"},
  "merchant_id": "number",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `200`: 获取成功
- `404`: 智能体不存在
- `403`: 无权限

### 5.3 获取智能体列表

**接口**: `GET /api/agents/`

**描述**: 获取当前商户的所有智能体列表

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
- `skip`: 跳过条数 (默认: 0)
- `limit`: 每页条数 (默认: 100)

**响应参数**: 
```json
[
  {
    "id": "number",
    "name": "string",
    "description": "string",
    "config": {"key": "value"},
    "merchant_id": "number",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  },
  ...
]
```

**状态码**: 
- `200`: 获取成功

### 5.4 更新智能体

**接口**: `PUT /api/agents/{agent_id}`

**描述**: 更新指定智能体的信息

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
```json
{
  "name": "string", // 可选
  "description": "string", // 可选
  "config": {"key": "value"}, // 可选
  "status": "string" // 可选
}
```

**响应参数**: 
```json
{
  "id": "number",
  "name": "string",
  "description": "string",
  "config": {"key": "value"},
  "merchant_id": "number",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `200`: 更新成功
- `404`: 智能体不存在
- `403`: 无权限

### 5.5 删除智能体

**接口**: `DELETE /api/agents/{agent_id}`

**描述**: 删除指定的智能体

**请求头**: 
- `Authorization: Bearer {token}`

**响应**: 无内容

**状态码**: 
- `204`: 删除成功
- `404`: 智能体不存在
- `403`: 无权限

## 6. 会话接口 (Sessions)

### 6.1 创建会话

**接口**: `POST /api/sessions/`

**描述**: 创建新的聊天会话

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
```json
{
  "title": "string",
  "user_id": "number",
  "agent_id": "number",
  "merchant_id": "number",
  "status": "string"
}
```

**响应参数**: 
```json
{
  "id": "string",
  "title": "string",
  "user_id": "number",
  "agent_id": "number",
  "merchant_id": "number",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "message_count": "number"
}
```

**状态码**: 
- `201`: 创建成功
- `403`: 无权限

### 6.2 获取会话详情

**接口**: `GET /api/sessions/{conversation_id}`

**描述**: 获取指定会话的详细信息

**请求头**: 
- `Authorization: Bearer {token}`

**响应参数**: 
```json
{
  "id": "string",
  "title": "string",
  "user_id": "number",
  "agent_id": "number",
  "merchant_id": "number",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "message_count": "number"
}
```

**状态码**: 
- `200`: 获取成功
- `404`: 会话不存在
- `403`: 无权限

### 6.3 获取会话列表

**接口**: `GET /api/sessions/`

**描述**: 获取当前用户的所有会话列表

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
- `skip`: 跳过条数 (默认: 0)
- `limit`: 每页条数 (默认: 100)

**响应参数**: 
```json
[
  {
    "id": "string",
    "title": "string",
    "user_id": "number",
    "agent_id": "number",
    "merchant_id": "number",
    "status": "string",
    "created_at": "string",
    "updated_at": "string",
    "message_count": "number"
  },
  ...
]
```

**状态码**: 
- `200`: 获取成功

### 6.4 更新会话

**接口**: `PUT /api/sessions/{conversation_id}`

**描述**: 更新指定会话的信息

**请求头**: 
- `Authorization: Bearer {token}`

**请求参数**: 
```json
{
  "title": "string", // 可选
  "agent_id": "number" // 可选
}
```

**响应参数**: 
```json
{
  "id": "string",
  "title": "string",
  "user_id": "number",
  "agent_id": "number",
  "merchant_id": "number",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "message_count": "number"
}
```

**状态码**: 
- `200`: 更新成功
- `404`: 会话不存在
- `403`: 无权限

### 6.5 删除会话

**接口**: `DELETE /api/sessions/{conversation_id}`

**描述**: 删除指定的会话

**请求头**: 
- `Authorization: Bearer {token}`

**响应**: 无内容

**状态码**: 
- `204`: 删除成功
- `404`: 会话不存在
- `403`: 无权限

## 7. 消息接口 (Messages)

### 7.1 创建消息

**接口**: `POST /api/messages/`

**描述**: 创建新的聊天消息

**请求头**: 
- `Authorization: Bearer {token}` (可选)

**请求参数**: 
```json
{
  "conversation_id": "string",
  "user_id": "number",
  "content": "string",
  "role": "string", // user 或 assistant
  "message_type": "string",
  "status": "string"
}
```

**响应参数**: 
```json
{
  "id": "number",
  "conversation_id": "string",
  "user_id": "number",
  "content": "string",
  "role": "string",
  "message_type": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `201`: 创建成功
- `500`: 服务器错误

### 7.2 获取消息详情

**接口**: `GET /api/messages/{message_id}`

**描述**: 获取指定消息的详细信息

**请求头**: 
- `Authorization: Bearer {token}` (可选)

**响应参数**: 
```json
{
  "id": "number",
  "conversation_id": "string",
  "user_id": "number",
  "content": "string",
  "role": "string",
  "message_type": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `200`: 获取成功
- `404`: 消息不存在
- `500`: 服务器错误

### 7.3 获取消息列表

**接口**: `GET /api/messages/`

**描述**: 获取指定会话的所有消息

**请求头**: 
- `Authorization: Bearer {token}` (可选)

**请求参数**: 
- `conversation_id`: 会话ID (必需)
- `skip`: 跳过条数 (默认: 0)
- `limit`: 每页条数 (默认: 100)
- `session_id`: 会话ID (兼容旧版本)

**响应参数**: 
```json
[
  {
    "id": "number",
    "conversation_id": "string",
    "user_id": "number",
    "content": "string",
    "role": "string",
    "message_type": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  },
  ...
]
```

**状态码**: 
- `200`: 获取成功
- `500`: 服务器错误

### 7.4 更新消息

**接口**: `PUT /api/messages/{message_id}`

**描述**: 更新指定消息的信息

**请求头**: 
- `Authorization: Bearer {token}` (可选)

**请求参数**: 
```json
{
  "content": "string", // 可选
  "role": "string", // 可选
  "message_type": "string", // 可选
  "status": "string" // 可选
}
```

**响应参数**: 
```json
{
  "id": "number",
  "conversation_id": "string",
  "user_id": "number",
  "content": "string",
  "role": "string",
  "message_type": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

**状态码**: 
- `200`: 更新成功
- `404`: 消息不存在
- `500`: 服务器错误

### 7.5 删除消息

**接口**: `DELETE /api/messages/{message_id}`

**描述**: 删除指定的消息

**请求头**: 
- `Authorization: Bearer {token}` (可选)

**响应**: 无内容

**状态码**: 
- `204`: 删除成功
- `404`: 消息不存在
- `500`: 服务器错误

## 8. 前端API调用示例

### 8.1 认证调用示例

```javascript
import { post } from '@/utils/request';

// 用户登录
export const login = (data) => {
  return post('/auth/login', data);
};

// 调用示例
async function handleLogin(username, password) {
  try {
    const res = await login({ username, password });
    const { access_token, userInfo } = res.data;
    // 存储token和用户信息
    localStorage.setItem('token', access_token);
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
    return res;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
}
```

### 8.2 聊天调用示例

```javascript
import { post } from '@/utils/request';

// 发送聊天消息
export const sendChatMessage = (data) => {
  return post('/chat/completions', data);
};

// 流式聊天处理示例
async function handleStreamChat(query, agentId, conversationId) {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api'}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        query,
        user_id: 1, // 当前用户ID
        merchant_id: 1, // 当前商户ID
        agent_id: agentId,
        conversation_id: conversationId
      }),
    });

    if (!response.ok) throw new Error('请求失败');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      // 处理接收到的数据块
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data:')) {
          const data = line.substring(5).trim();
          if (data === '[DONE]') break;
          try {
            const json = JSON.parse(data);
            if (json.event === 'message') {
              result += json.answer || json.content;
              // 实时更新UI
              updateChatUI(result);
            }
          } catch (e) {
            console.error('解析错误:', e);
          }
        }
      }
    }
    
    return result;
  } catch (error) {
    console.error('聊天失败:', error);
    throw error;
  }
}
```

## 9. API调用错误处理

前端API调用错误处理遵循以下规则：

1. **401 未授权错误**：自动清除token并重定向到登录页面
2. **404 资源不存在**：显示资源不存在提示
3. **403 权限错误**：显示无权限操作提示
4. **500 服务器错误**：显示服务器错误提示
5. **网络错误**：显示网络连接失败提示

```javascript
// 请求拦截器处理示例
instance.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器处理示例
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理401未授权错误
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 10. 接口版本管理

当前API版本为v1，后续版本更新将在URL中添加版本标识，如：`/api/v2/chat/completions`。

## 11. 安全规范

1. 所有API接口必须使用HTTPS协议（生产环境）
2. 敏感数据传输必须加密
3. 认证token必须妥善保管，避免泄露
4. 定期更换密码和API密钥
5. 遵循最小权限原则，严格控制API访问权限

## 12. 附录：数据结构定义

### 12.1 用户 (User)
```typescript
interface User {
  id: number;
  username: string;
  email?: string;
  merchant_id: number;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
}
```

### 12.2 智能体 (Agent)
```typescript
interface Agent {
  id: number;
  name: string;
  description?: string;
  config: Record<string, any>;
  merchant_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}
```

### 12.3 会话 (Conversation)
```typescript
interface Conversation {
  id: string;
  title: string;
  user_id: number;
  agent_id: number;
  merchant_id: number;
  status: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}
```

### 12.4 消息 (Message)
```typescript
interface Message {
  id: number;
  conversation_id: string;
  user_id: number;
  content: string;
  role: string;
  message_type: string;
  status: string;
  created_at: string;
  updated_at: string;
}
```