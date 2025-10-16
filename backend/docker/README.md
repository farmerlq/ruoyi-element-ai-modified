# 问客项目后端Docker部署说明

本目录包含问客项目后端服务的Docker部署配置文件，用于快速搭建完整的开发或生产环境。

## 部署文件说明

- `docker-compose.yml`: Docker Compose配置文件，定义了后端服务和PostgreSQL数据库服务
- `init_db.sql`: 数据库初始化脚本，包含创建表结构和默认数据
- `.env.example`: 环境变量配置模板
- `../Dockerfile`: 后端服务Docker镜像构建文件

## 环境要求

- Docker: 20.10.0+ 
- Docker Compose: 1.29.0+

## 快速开始

### 1. 准备环境变量

复制 `.env.example` 文件并重命名为 `.env`，然后根据实际需求修改配置：

```bash
cp .env.example .env
# 编辑.env文件
```

**重要配置项说明：**
- `SECRET_KEY`: 用于JWT认证的密钥，请设置为安全的随机字符串
- `OPENAI_API_KEY`: OpenAI API密钥，用于AI模型调用
- `DIFY_API_BASE_URL`: Dify服务的基础URL

### 2. 构建和启动服务

在`backend/docker`目录下执行以下命令：

```bash
docker-compose up -d --build
```

该命令会：
- 构建后端服务镜像
- 拉取并启动PostgreSQL数据库
- 初始化数据库表结构和默认数据
- 启动后端API服务

### 3. 验证服务是否正常运行

检查容器状态：
```bash
docker-compose ps
```

查看服务日志：
```bash
docker-compose logs web
```

访问API文档：
打开浏览器，访问 http://localhost:8000/docs 查看Swagger UI接口文档

健康检查：
服务提供健康检查端点，可以通过 http://localhost:8000/health 进行访问

### 4. 默认登录凭据

系统初始化时会创建默认管理员账户：
- 用户名: admin
- 密码: admin123

## 常用命令

- 启动服务：`docker-compose up -d`
- 停止服务：`docker-compose down`
- 查看日志：`docker-compose logs -f`
- 重启服务：`docker-compose restart`
- 进入数据库容器：`docker-compose exec db psql -U wenke_user -d wenke_db`

## 数据持久化

- 数据库数据通过Docker卷`postgres_data`持久化存储
- 后端服务日志通过绑定挂载到`./logs`目录

## 开发环境配置

在开发环境中，可以修改`.env`文件中的`DEBUG=True`以启用调试模式，同时可以考虑将本地代码目录映射到容器中以便实时查看代码变更效果。

## 生产环境配置

在生产环境中，建议：
- 使用更安全的`SECRET_KEY`
- 禁用`DEBUG`模式
- 修改默认的数据库密码
- 配置适当的网络安全策略
- 添加SSL证书以支持HTTPS

## 故障排查

如果服务无法正常启动，请检查：
1. 环境变量配置是否正确
2. 端口是否被其他应用占用
3. Docker和Docker Compose版本是否符合要求
4. 查看容器日志以获取详细错误信息

## 联系信息

如有问题，请联系项目维护人员。