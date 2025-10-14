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
from models.message import Message
from models.session import Conversation
import uuid

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
    thought_content = ""   # 收集思考内容
    full_message_content = ""  # 收集完整的消息内容
    message_events_received = set()  # 用于跟踪已接收的消息事件ID，避免重复
    
    try:
        # 实时转发所有流式响应事件
        async for response in chat_service.chat_stream(request):
            # 统计信息
            event_count += 1
            
            if response.metadata and 'event' in response.metadata:
                # 如果是Dify原生事件，直接发送metadata
                event_type = response.metadata.get('event')
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                # 为消息事件生成唯一标识符
                message_event_id = None
                if event_type in ['text_chunk', 'message', 'agent_message'] and response.message_id:
                    message_event_id = f"{event_type}:{response.message_id}"
                
                # 收集工作流事件用于token统计和保存（不包括agent_thought事件）
                if event_type and event_type != "agent_thought" and ("workflow" in event_type or "node" in event_type or event_type in ["message_end", "message_file"]):
                    workflow_events.append(response.metadata)
                
                # 收集思考内容（仅针对agent_thought事件）
                if event_type == "agent_thought":
                    thought_data = response.metadata
                    # 获取完整的思考内容（如果有的话）
                    full_thought_content = thought_data.get("full_thought_content", "")
                    if full_thought_content and full_thought_content.strip():
                        thought_content += full_thought_content + "\n"
                    else:
                        # 构建思考内容文本
                        thought_text = thought_data.get("thought", "")
                        if not thought_text:
                            thought_text = thought_data.get("observation", "")
                        
                        # 添加工具调用信息（如果有的话）
                        if thought_data.get("tool") and thought_data.get("tool_input"):
                            try:
                                tool_input = thought_data.get("tool_input")
                                if isinstance(tool_input, str):
                                    tool_input = json.loads(tool_input)
                                thought_text += f"\n\n[工具调用: {thought_data['tool']}]\n"
                                thought_text += f"参数: {json.dumps(tool_input, ensure_ascii=False, indent=2)}\n"
                            except Exception:
                                # 如果tool_input不是有效的JSON，直接添加
                                thought_text += f"\n\n[工具调用: {thought_data['tool']}]\n"
                                thought_text += f"参数: {thought_data.get('tool_input', '')}\n"
                        
                        # 添加文件引用信息（如果有的话）
                        if thought_data.get("message_files") and isinstance(thought_data["message_files"], list):
                            thought_text += "\n\n[文件引用]:\n"
                            for i, file in enumerate(thought_data["message_files"], 1):
                                thought_text += f"{i}. {file}\n"
                        
                        # 添加文件ID信息（如果有的话）
                        if thought_data.get("file_id"):
                            thought_text += f"\n\n[文件ID]: {thought_data['file_id']}\n"
                        
                        # 只有当thought_text有实际内容时才添加到thought_content中
                        if thought_text and thought_text.strip():
                            thought_content += thought_text + "\n"
                
                event_data = response.metadata.copy()
                # 对于text_chunk/message/agent_message事件，确保包含content字段
                if event_data.get('event') in ['text_chunk', 'message', 'agent_message'] and response.message:
                    event_data['content'] = response.message
                    # 统计所有消息内容长度
                    total_message_length += len(response.message)
                    total_data_length += len(response.message)  # 统计数据内容
                    # 收集消息内容（避免重复）
                    message_event_key = f"{event_data.get('event')}_{response.message_id or ''}"
                    if message_event_key not in message_events_received:
                        message_events_received.add(message_event_key)
                        full_message_content += response.message
                
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
                # 收集消息内容
                full_message_content += message_content
                
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
        
        # 计算聊天接口的token：输入query长度 + 输出消息长度（按4字符=1token估算）
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
        
        # 保存统计信息到数据库，确保前端显示和数据库保存的数据一致
        # 注意：这里我们使用的是前端显示的total_tokens_estimated和cost
        try:
            # 保存统计信息到数据库
            save_chat_statistics(db, request, total_tokens_estimated, cost, workflow_events, thought_content, full_message_content)
        except Exception as e:
            logging.error(f"Error saving chat statistics to database: {e}")
        
        # 输出详细统计信息到日志
        logging.info(f"📊 聊天接口统计: 总共处理了 {event_count} 个事件")
        logging.info(f"📊 事件类型分布: {event_types}")
        logging.info(f"📊 总消息长度: {total_message_length} 字符")
        logging.info(f"📊 所有数据内容总长度: {total_data_length} 字符 (包括metadata和消息内容)")
        logging.info(f"📊 完整SSE数据总长度: {total_sse_length} 字符 (包括data:前缀和换行符)")
        logging.info(f"📊 总传输数据量: {total_transfer_data} 字符 (SSE数据 + 消息内容)")
        logging.info(f"📊 Dify API返回token数: {dify_tokens} tokens")
        logging.info(f"📊 聊天接口输入token数: {input_tokens} tokens (query: '{input_query[:30]}{'...' if len(input_query) > 30 else ''}')")
        logging.info(f"📊 聊天接口输出token数: {output_tokens} tokens")
        logging.info(f"📊 总token数: {total_tokens} tokens (Dify API + 聊天接口)")
        logging.info(f"📊 估算总token数: {total_tokens_estimated} tokens (基于传输数据量)")
        if total_tokens_estimated > 0:
            logging.info(f"📊 预估费用: ¥{cost:.6f} (按每百万token 12元计算)")
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def save_chat_statistics(db: Session, request: ChatRequest, total_tokens_estimated: int, cost: float, workflow_events: list, thought_content: str, full_message_content: str = ""):
    """保存聊天统计数据到数据库"""
    try:
        # 生成对话ID（如果有会话ID，强制使用传参的会话ID；如果没有会话ID就可以有解析出来的会话ID；如果都没有的话就新建会话ID）
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # 保存或更新对话
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                id=conversation_id,
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                title=request.get_query_text()[:100],  # 使用前100个字符作为标题
                status="active"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        elif request.conversation_id and request.conversation_id != conversation_id:
            # 更新对话的更新时间
            # 不需要手动设置 updated_at = None，SQLAlchemy 会自动处理
            db.commit()
        
        # 检查是否已经存在相同对话ID的用户消息，避免重复保存
        existing_user_message = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "user",
            Message.content == (request.get_query_text() or "")
        ).first()
        
        # 只有当不存在相同用户消息时才保存用户消息
        if not existing_user_message:
            # 保存用户消息
            user_query = request.get_query_text() or ""
            
            user_message = Message(
                conversation_id=conversation_id,
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                role="user",
                content=user_query
            )
            db.add(user_message)
        
        # 检查是否已经存在相同对话ID的AI消息，避免重复保存
        existing_ai_message = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "agent"
        ).order_by(Message.id.desc()).first()
        
        # 只有当不存在相同AI消息时才保存AI回复消息
        if not existing_ai_message:
            # 保存AI回复消息
            ai_message = Message(
                conversation_id=conversation_id,
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                role="agent",
                content=full_message_content,  # 保存完整的消息内容
                # 正确处理JSON格式的thought_content
                thought_content=thought_content if isinstance(thought_content, dict) or isinstance(thought_content, list) else (thought_content if thought_content and thought_content.strip() else None),
                workflow_events=workflow_events if workflow_events else None,
                cost=cost,
                total_tokens=total_tokens_estimated,  # 使用前端显示的估算值
                total_tokens_estimated=total_tokens_estimated
            )
            db.add(ai_message)
        
        db.commit()
    except Exception as e:
        # 记录错误但不中断流式传输
        logging.error(f"保存消息到数据库时出错: {e}")
        db.rollback()


async def generate_chat_response(request: ChatRequest, db: Session, current_user: User) -> ChatResponse:
    """生成非流式聊天响应"""
    # 使用ChatService处理非流式响应
    chat_service = ChatService(db)
    response = await chat_service.chat(request)
    
    # 确保响应中包含费用和token估算信息
    if not hasattr(response, 'estimated_cost') or response.estimated_cost is None:
        # 计算费用（按照每百万token 12元的价格）
        if response.total_tokens_estimated:
            response.estimated_cost = (response.total_tokens_estimated / 1000000) * 12
        else:
            response.estimated_cost = 0.0
    
    return response


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
        # 注意：需要确保config_dict中的stream参数是布尔类型
        stream_setting = agent.config_dict.get("stream")
        should_stream = False
        if isinstance(stream_setting, bool):
            should_stream = stream_setting
        elif isinstance(stream_setting, str):
            should_stream = stream_setting.lower() == "true"
        elif isinstance(stream_setting, (int, float)):
            should_stream = bool(stream_setting)
        
        if should_stream:
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