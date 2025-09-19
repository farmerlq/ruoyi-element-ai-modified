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
    
    # 统计变量
    event_count = 0
    event_types = {}
    total_message_length = 0
    total_data_length = 0  # 统计所有数据内容长度
    total_sse_length = 0   # 新增：统计完整的SSE数据长度（包括data:前缀）
    total_tokens = 0
    workflow_events = []
    
    try:
        # 实时转发所有流式响应事件
        async for response in chat_service.chat_stream(request):
            # 统计信息
            event_count += 1
            
            if response.metadata and 'event' in response.metadata:
                # 如果是Dify原生事件，直接发送metadata
                event_type = response.metadata.get('event')
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                # 收集工作流事件用于token统计
                if event_type and ("workflow" in event_type or "node" in event_type):
                    workflow_events.append(response.metadata)
                
                event_data = response.metadata.copy()
                # 对于text_chunk事件，确保包含content字段
                if event_data.get('event') == 'text_chunk' and response.message:
                    event_data['content'] = response.message
                    # 统计所有消息内容长度
                    total_message_length += len(response.message)
                    total_data_length += len(response.message)  # 统计数据内容
                
                # 统计所有事件类型的metadata数据长度
                metadata_json = json.dumps(response.metadata)
                total_data_length += len(metadata_json)
                
                # 生成SSE格式数据并统计完整长度
                sse_data = f"data: {json.dumps(event_data)}\n\n"
                total_sse_length += len(sse_data)  # 统计完整的SSE数据长度
                
                yield sse_data
            elif response.message:
                # 对于普通消息，转换为Dify的message事件格式
                message_content = response.message or ""
                # 统计所有消息内容长度
                total_message_length += len(message_content)
                total_data_length += len(message_content)  # 统计数据内容
                
                dify_event = {
                    "event": "message",
                    "answer": message_content,
                    "task_id": response.message_id or "",
                    "id": response.message_id or "",
                    "created_at": int(datetime.now().timestamp())
                }
                
                # 统计message事件的metadata数据长度
                metadata_json = json.dumps(dify_event)
                total_data_length += len(metadata_json)
                
                # 生成SSE格式数据并统计完整长度
                sse_data = f"data: {json.dumps(dify_event)}\n\n"
                total_sse_length += len(sse_data)  # 统计完整的SSE数据长度
                
                yield sse_data
        
        # 计算总token数：Dify API返回的token + 聊天接口输入输出的token
        dify_tokens = 0
        for event in workflow_events:
            if event.get("event") == "message_end" and event.get("usage"):
                usage_info = event.get("usage")
                dify_tokens = usage_info.get("total_tokens", 0)
                break
            elif event.get("event") == "workflow_finished" and event.get("total_tokens"):
                dify_tokens = event.get("total_tokens", 0)
                break
        
        # 计算聊天接口的token：输入query长度 + 输出消息长度（按4个字符=1个token估算）
        input_query = request.get_query_text() or ""
        input_tokens = max(1, len(input_query) // 4)  # 至少1个token
        output_tokens = max(1, total_message_length // 4)  # 至少1个token
        chat_interface_tokens = input_tokens + output_tokens
        
        # 总token数 = Dify API token + 聊天接口token
        total_tokens = dify_tokens + chat_interface_tokens
        
        # 计算费用 - 基于网络传输的实际数据量
        # 总传输数据量 = 完整SSE数据总长度 + 消息内容长度
        total_transfer_data = total_sse_length + total_message_length
        # 按4个字符=1个token估算，计算总token数
        total_tokens_estimated = max(1, total_transfer_data // 4)
        # 费用计算：按每百万token 12元
        cost = (total_tokens_estimated / 1000000) * 12 if total_tokens_estimated > 0 else 0.0
        
        # 发送统计信息事件
        stats_event = {
            "event": "statistics",
            "event_count": event_count,
            "event_types": event_types,
            "total_message_length": total_message_length,
            "total_data_length": total_data_length,
            "total_sse_length": total_sse_length,
            "total_transfer_data": total_transfer_data,
            "dify_tokens": dify_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "total_tokens_estimated": total_tokens_estimated,
            "total_cost": cost,
            "estimated_cost": cost
        }
        yield f"data: {json.dumps(stats_event)}\n\n"
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
        
        # 输出详细统计信息
        print(f"📊 聊天接口统计: 总共处理了 {event_count} 个事件")
        print(f"📊 事件类型分布: {event_types}")
        print(f"📊 总消息长度: {total_message_length} 字符")
        print(f"📊 所有数据内容总长度: {total_data_length} 字符 (包括metadata和消息内容)")
        print(f"📊 完整SSE数据总长度: {total_sse_length} 字符 (包括data:前缀和换行符)")
        print(f"📊 总传输数据量: {total_transfer_data} 字符 (SSE数据 + 消息内容)")
        print(f"📊 Dify API返回token数: {dify_tokens} tokens")
        print(f"📊 聊天接口输入token数: {input_tokens} tokens (query: '{input_query[:30]}{'...' if len(input_query) > 30 else ''}')")
        print(f"📊 聊天接口输出token数: {output_tokens} tokens")
        print(f"📊 总token数: {total_tokens} tokens (Dify API + 聊天接口)")
        print(f"📊 估算总token数: {total_tokens_estimated} tokens (基于传输数据量)")
        if total_tokens_estimated > 0:
            print(f"📊 预估费用: ¥{cost:.6f} (按每百万token 12元计算)")
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def generate_chat_response(request: ChatRequest, db: Session, current_user: User) -> ChatResponse:
    """生成非流式聊天响应"""
    chat_service = ChatService(db)
    
    try:
        response = await chat_service.chat(request)
        
        # 对于非流式响应，我们需要估算token数和费用
        # 基于请求和响应内容进行估算
        input_query = request.get_query_text() or ""
        output_message = response.message or ""
        
        # 计算输入输出token数（按4字符=1token估算）
        input_tokens = max(1, len(input_query) // 4)
        output_tokens = max(1, len(output_message) // 4)
        total_tokens_estimated = input_tokens + output_tokens
        
        # 计算费用（按每百万token 12元）
        cost = (total_tokens_estimated / 1000000) * 12 if total_tokens_estimated > 0 else 0.0
        
        # 构建响应，包含估算的token数和费用
        response.total_tokens_estimated = total_tokens_estimated
        response.estimated_cost = cost
        
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
        if agent.config_dict.get("stream", False):
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
