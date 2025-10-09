# 问客项目 - 智能客服系统

## 1. 项目概述

问客项目是一个基于AI技术的智能客服系统，旨在为企业提供高效、智能的客户服务解决方案。系统采用前后端分离架构，结合先进的大语言模型，实现智能问答、会话管理和客户服务自动化等功能。

### 1.1 主要功能

- **智能问答**：基于大语言模型的智能回复，支持上下文理解和流式响应
- **会话管理**：创建、查看、更新和删除用户会话，支持多轮对话
- **智能体管理**：配置和管理不同功能的智能客服机器人
- **消息管理**：记录和管理用户与智能体之间的所有对话消息
- **用户认证与授权**：安全的用户登录、权限控制和会话管理

### 1.2 典型应用场景

- 企业客户服务自动化
- 在线咨询和帮助中心
- 产品售前咨询和售后支持
- 智能知识库问答系统
- 多渠道客户互动平台

## 2. 项目结构

项目采用清晰的前后端分离架构，分为`backend`（后端）和`frontend`（前端）两个主要目录。后端基于FastAPI构建，提供RESTful API接口；前端采用Vue 3 + TypeScript开发，提供现代化的用户界面。

```
├── backend/                 # 后端项目目录
│   ├── main.py              # FastAPI应用入口
│   ├── requirements.txt     # Python依赖文件
│   ├── docker/              # Docker部署配置
│   │   ├── Dockerfile       # 后端Docker构建文件
│   │   ├── docker-compose.yml # Docker编排配置
│   │   ├── init_db.sql      # 数据库初始化脚本
│   │   ├── .env.example     # 环境变量示例文件
│   │   └── README.md        # Docker部署说明
│   ├── routers/             # API路由定义
│   │   ├── auth.py          # 认证相关接口
│   │   ├── chat.py          # 聊天相关接口
│   │   ├── agents.py        # 智能体管理接口
│   │   ├── sessions.py      # 会话管理接口
│   │   └── messages.py      # 消息管理接口
│   ├── models/              # 数据模型定义
│   ├── schemas/             # 请求和响应数据结构
│   └── utils/               # 工具函数
├── frontend/                # 前端项目目录
│   ├── package.json         # NPM依赖文件
│   ├── src/                 # 前端源码
│   │   ├── main.ts          # Vue应用入口
│   │   ├── App.vue          # 根组件
│   │   ├── components/      # 公共组件
│   │   ├── pages/           # 页面组件
│   │   ├── api/             # API调用封装
│   │   ├── utils/           # 工具函数
│   │   └── stores/          # Pinia状态管理
│   └── vite.config.ts       # Vite配置文件
├── API_DOCUMENTATION.md     # API接口文档
└── README.md                # 项目说明文档
```

## 3. 技术栈

### 3.1 后端技术

- **Python 3.11**：主要编程语言
- **FastAPI**：高性能Web框架，用于构建API接口
- **SQLAlchemy**：ORM数据库工具
- **PostgreSQL 15**：关系型数据库，存储用户、会话、消息等数据
- **JWT**：用于用户认证和授权
- **Uvicorn**：ASGI服务器，运行FastAPI应用
- **Docker**：容器化部署工具

### 3.2 前端技术

- **Vue 3**：现代前端框架，用于构建用户界面
- **TypeScript**：JavaScript超集，提供类型安全
- **Vite**：现代化的前端构建工具
- **Pinia**：Vue的状态管理库
- **Axios**：HTTP客户端，用于API调用
- **Vue Router**：路由管理
- **Ant Design Vue**：UI组件库（或其他自定义组件）

### 3.3 AI集成

- **OpenAI API**：集成大语言模型，提供智能问答能力
- **流式响应处理**：支持SSE（Server-Sent Events）实现实时对话体验

## 4. 环境要求

### 4.1 开发环境

- **后端**：
  - Python 3.11或更高版本
  - PostgreSQL 15或更高版本
  - pip 23.0或更高版本
  - Git

- **前端**：
  - Node.js 18或更高版本
  - npm 9或更高版本
  - 现代浏览器（Chrome、Firefox、Safari、Edge）

### 4.2 生产环境

- Docker和Docker Compose（推荐）
- 或：
  - Python 3.11+运行环境
  - PostgreSQL 15+数据库
  - Nginx或其他Web服务器（用于前端静态文件和API代理）

## 5. 快速开始

### 5.1 使用Docker Compose快速部署（推荐）

1. 克隆项目代码

```bash
git clone <repository-url>
cd 问客项目001
```

2. 进入后端docker目录

```bash
cd backend/docker
```

3. 复制并配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，设置数据库密码、JWT密钥等配置
```

4. 启动服务

```bash
docker-compose up -d --build
```

5. 验证服务运行状态

```bash
docker-compose ps
# 检查所有服务是否正常运行
```

6. 访问应用

- 前端应用：http://localhost:3000
- 后端API文档：http://localhost:8000/docs

### 5.2 本地开发环境设置

#### 5.2.1 后端设置

1. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

2. 配置PostgreSQL数据库

创建数据库和用户：

```sql
CREATE DATABASE wenke;
CREATE USER wenke_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE wenke TO wenke_user;
```

3. 设置环境变量

创建`.env`文件并添加以下内容：

```
POSTGRES_USER=wenke_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=wenke
DATABASE_URL=postgresql://wenke_user:your_password@localhost/wenke
JWT_SECRET_KEY=your_jwt_secret_key
DEBUG=True
OPENAI_API_KEY=your_openai_api_key
```

4. 初始化数据库

```bash
python init_db.py
```

5. 启动后端服务

```bash
uvicorn main:app --reload --port 8000
```

#### 5.2.2 前端设置

1. 安装NPM依赖

```bash
cd frontend
npm install
```

2. 配置环境变量

创建`.env.local`文件并添加以下内容：

```
VITE_API_BASE_URL=http://localhost:8000/api
```

3. 启动前端开发服务器

```bash
npm run dev
```

4. 访问应用

打开浏览器，访问：http://localhost:3000

## 6. 核心功能模块

### 6.1 用户认证与授权

系统实现了基于JWT的用户认证机制，包括用户登录、信息查询和令牌验证等功能。认证成功后，用户可以访问受保护的API端点。

### 6.2 智能体管理

管理员用户可以创建、配置和管理多个智能客服机器人，每个智能体可以有不同的配置参数和响应行为。智能体配置存储在数据库中，可以随时修改和更新。

### 6.3 会话管理

用户可以创建多个聊天会话，每个会话关联一个智能体。系统支持会话列表查看、会话详情获取、会话标题修改和会话删除等操作。

### 6.4 消息管理

系统记录所有用户与智能体之间的对话消息，包括消息内容、发送者角色、发送时间等信息。支持消息的查询、更新和删除操作。

### 6.5 智能聊天

系统核心功能，支持用户与智能体进行实时对话。主要特点：

- **流式响应**：采用SSE（Server-Sent Events）技术，实现实时打字机效果
- **上下文理解**：支持多轮对话，智能体能够理解对话上下文
- **成本估算**：提供对话的token使用量和成本估算
- **错误处理**：完善的异常处理机制，确保对话流畅进行

## 7. API文档

系统提供了详细的API接口文档，支持交互式测试：

- **Swagger UI**：http://localhost:8000/docs（开发环境）
- **ReDoc**：http://localhost:8000/redoc（开发环境）
- **项目文档**：`API_DOCUMENTATION.md`（本地文件）

API文档包含了所有可用的接口、请求参数、响应格式和错误处理等详细信息，便于前后端开发人员协作和集成。

## 8. 数据持久化

系统使用PostgreSQL数据库存储所有业务数据，主要数据表包括：

- **merchants**：商户信息表
- **users**：用户信息表
- **agents**：智能体配置表
- **sessions**：会话记录表
- **messages**：消息记录表

在Docker部署模式下，数据库数据通过Docker卷进行持久化存储，确保数据不会丢失。

## 9. 开发指南

### 9.1 后端开发流程

1. 创建新的路由文件或修改现有路由文件（位于`backend/routers/`目录）
2. 定义数据模型（位于`backend/models/`目录）
3. 定义请求和响应模式（位于`backend/schemas/`目录）
4. 实现业务逻辑和数据操作
5. 编写单元测试和集成测试
6. 通过`/docs`接口文档测试API功能

### 9.2 前端开发流程

1. 创建新的组件或页面（位于`frontend/src/components/`或`frontend/src/pages/`目录）
2. 在`frontend/src/api/`目录下封装对应的API调用
3. 使用Pinia进行状态管理（位于`frontend/src/stores/`目录）
4. 实现组件的交互逻辑和数据展示
5. 进行响应式设计和用户体验优化
6. 运行`npm run build`验证构建是否成功

## 10. 部署指南

### 10.1 Docker部署

详见`backend/docker/README.md`文件，包含了完整的Docker部署说明、环境变量配置和常用命令。

### 10.2 传统部署

1. **后端部署**：
   - 使用Gunicorn和Uvicorn部署FastAPI应用
   - 配置Nginx作为反向代理
   - 设置Systemd服务确保应用自动启动

2. **前端部署**：
   - 执行`npm run build`构建生产版本
   - 将构建产物部署到Nginx或其他Web服务器
   - 配置Nginx反向代理API请求

3. **数据库配置**：
   - 配置PostgreSQL生产环境
   - 设置定期备份策略
   - 优化数据库性能参数

## 11. 安全性考虑

- **认证和授权**：使用JWT进行身份验证，严格控制API访问权限
- **数据加密**：敏感数据传输采用HTTPS协议加密
- **输入验证**：对所有用户输入进行严格验证和清洗
- **防止SQL注入**：使用参数化查询和ORM框架
- **错误处理**：避免泄露系统内部信息的错误消息
- **CORS配置**：合理配置跨域资源共享策略

## 12. 性能优化

- **数据库索引**：对常用查询字段添加索引
- **缓存机制**：考虑引入Redis缓存热点数据
- **异步处理**：使用FastAPI的异步特性处理IO密集型任务
- **分页查询**：API实现分页功能，避免一次性返回大量数据
- **前端优化**：组件懒加载、代码分割、图片优化等

## 13. 故障排查

### 13.1 常见问题及解决方案

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证数据库连接字符串是否正确
   - 确认数据库用户权限是否足够

2. **API认证失败**
   - 检查JWT令牌是否过期
   - 验证令牌签名是否正确
   - 确认用户角色权限是否匹配

3. **聊天响应缓慢**
   - 检查OpenAI API连接状态
   - 优化提示词设计
   - 考虑使用模型缓存

4. **Docker容器运行异常**
   - 查看容器日志：`docker-compose logs -f`
   - 检查环境变量配置
   - 确认端口映射和网络配置正确

### 13.2 日志系统

- 后端日志：FastAPI应用日志，包含API请求、错误信息等
- 数据库日志：PostgreSQL数据库操作日志
- 容器日志：Docker容器运行日志

## 14. 未来规划

### 14.1 功能增强

- 多渠道接入：支持微信、网站、APP等多渠道客户服务
- 知识库管理：实现智能知识库的创建、更新和检索
- 多语言支持：扩展系统支持多语言对话能力
- 数据分析：添加客户服务数据统计和分析功能
- 自定义流程：支持配置复杂的客户服务流程

### 14.2 技术优化

- 微服务架构：将系统拆分为多个微服务，提高扩展性
- 缓存系统：引入分布式缓存，提高系统响应速度
- 消息队列：使用消息队列处理异步任务，提高系统稳定性
- A/B测试：支持不同模型和配置的A/B测试功能

## 15. 贡献指南

我们欢迎社区成员贡献代码和改进建议。贡献流程：

1. Fork项目仓库
2. 创建功能分支
3. 提交代码修改
4. 运行测试确保代码质量
5. 创建Pull Request
6. 等待代码审核和合并

## 16. 版权和许可

[MIT License](https://opensource.org/licenses/MIT)

## 17. 联系方式

如有问题或建议，请联系项目维护团队：

- 邮箱：contact@wenke.com
- GitHub Issues：https://github.com/wenke-project/issues
- 项目官网：https://www.wenke.com