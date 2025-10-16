from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import engine, Base
from routers import agents, merchants, users, sessions, messages, auth, chat
import argparse

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="问客AI平台API",
    description="问客AI平台提供了一套完整的API接口，用于管理商户、用户、智能体以及进行AI对话交互。",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_origin_regex="https?://.*"
)

@app.get("/")
async def root():
    return {"message": "欢迎使用问客AI平台API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health_check():
    return {"status": "healthy"}

# FastAPI的CORS中间件已经足够处理CORS请求，不需要额外的处理

# 包含路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(merchants.router, prefix="/api/v1/merchants", tags=["merchants"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)