from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import AsyncGenerator
import json
import logging
from datetime import datetime
from core.database import get_db
from core.deps import get_current_user_or_raise
from core.chat_service import ChatService
from core.adapter import ChatRequest, ChatResponse
from models.user import User
from models.agent import Agent

router = APIRouter(tags=["chat"])

async def stream_chat_response(request: ChatRequest, db: Session, current_user: User) -> AsyncGenerator[str, None]:
    """生成流式聊天响应"""
    chat_service = ChatService(db)
    
    try:
        async for response in chat_service.chat_stream(request):
            # 将响应转换为Dify原生SSE格式（前端期望的格式）
            if response.metadata and 'event' in response.metadata:
                # 如果是Dify原生事件，直接发送metadata
                event_data = response.metadata.copy()
                # 对于text_chunk事件，确保包含content字段
                if event_data.get('event') == 'text_chunk' and response.message:
                    event_data['content'] = response.message
                yield f"data: {json.dumps(event_data)}\n\n"
            else:
                # 对于普通消息，转换为Dify的message事件格式
                dify_event = {
                    "event": "message",
                    "answer": response.message or "",
                    "task_id": response.message_id or "",
                    "id": response.message_id or "",
                    "created_at": int(datetime.now().timestamp())
                }
                yield f"data: {json.dumps(dify_event)}\n\n"
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def generate_chat_response(request: ChatRequest, db: Session, current_user: User) -> ChatResponse:
    """生成非流式聊天响应"""
    chat_service = ChatService(db)
    
    try:
        response = await chat_service.chat(request)
        return response
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in generate_chat_response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/completions")
async def chat_completion(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise)  # 启用认证
):
    """
    处理聊天完成请求（根据智能体配置决定流式或非流式）
    """
    try:
        # 获取agent信息以确定流式设置
        agent = db.query(Agent).filter(Agent.id == request.agent_id).first()
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        
        # 根据智能体配置中的stream参数决定返回类型
        if agent.config and agent.config.get("stream", False):
            return StreamingResponse(
                stream_chat_response(request, db, current_user),
                media_type="text/event-stream"
            )
        else:
            # 非流式响应
            response = await generate_chat_response(request, db, current_user)
            return response
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/completions/stream")
async def chat_completion_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise)  # 启用认证
):
    """
    处理聊天完成请求（强制流式）
    """
    try:
        # 确保请求是流式的
        request.stream = True
        chat_service = ChatService(db)
        
        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                async for response in chat_service.chat_stream(request):
                    # 将响应转换为Dify原生SSE格式（前端期望的格式）
                    if response.metadata and 'event' in response.metadata:
                        # 如果是Dify原生事件，直接发送metadata
                        event_data = response.metadata.copy()
                        # 对于text_chunk事件，确保包含content字段
                        if event_data.get('event') == 'text_chunk' and response.message:
                            event_data['content'] = response.message
                        yield f"data: {json.dumps(event_data)}\n\n"
                    else:
                        # 对于普通消息，转换为Dify的message事件格式
                        dify_event = {
                            "event": "message",
                            "answer": response.message or "",
                            "task_id": response.message_id or "",
                            "id": response.message_id or "",
                            "created_at": int(datetime.now().timestamp())
                        }
                        yield f"data: {json.dumps(dify_event)}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Encoding": "none",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
