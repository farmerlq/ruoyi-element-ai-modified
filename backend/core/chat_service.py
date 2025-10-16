from typing import Dict, Any, AsyncGenerator, Optional
from sqlalchemy.orm import Session
from core.adapter import AdapterFactory, ChatRequest, ChatResponse
from models.agent import Agent
from models.session import Conversation
from models.message import Message
import asyncio
import uuid
import re
import inspect
import json

class ChatService:
    """聊天服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        # 获取agent信息
        agent = self.db.query(Agent).filter(Agent.id == request.agent_id).first()
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        
        # 根据智能体type字段判断是用哪个平台的适配器
        adapter_type: str = str(agent.type)
        
        # 使用智能体的配置（config）创建适配器
        agent_config_dict = agent.config_dict
        adapter_config = dict[str, Any]()
        for key, value in agent_config_dict.items():
            adapter_config[key] = value
        
        # 确保配置中包含必要的参数
        if "api_key" not in adapter_config:
            adapter_config["api_key"] = agent.config_dict.get("api_key", "")
        
        # 创建适配器
        adapter = AdapterFactory.create_adapter(adapter_type, adapter_config)
        
        try:
            # 执行普通聊天
            response = await adapter.chat(request)
            
            # 计算估算的token数（包括网络传输数据）
            input_query = request.get_query_text() or ""
            output_message = response.message or ""
            
            # 计算输入输出token数（按4字符=1token估算）
            input_tokens = max(1, len(input_query) // 4)
            output_tokens = max(1, len(output_message) // 4)
            # 计算完整的传输数据长度（包括JSON结构）
            response_json = json.dumps({
                "message": response.message,
                "conversation_id": response.conversation_id,
                "message_id": response.message_id,
                "metadata": response.metadata
            })
            response_data_length = len(response_json)
            
            # 总传输数据长度 = 输入查询长度 + 响应数据长度
            total_transfer_data = len(input_query) + response_data_length
            
            # 估算总token数（基于传输数据量）
            total_tokens_estimated = max(1, total_transfer_data // 4)
            
            # 将估算的token数添加到响应中
            response.total_tokens_estimated = total_tokens_estimated
            
            # 保存对话和消息到数据库
            self._save_conversation_and_message(request, response, agent)
            
            return response
        finally:
            # 关闭适配器连接（如果有的话）
            # BaseAdapter定义了close抽象方法，所以我们可以安全地调用它
            try:
                await adapter.close()
            except Exception as e:
                pass
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """处理流式聊天请求"""
        # 获取agent信息
        agent = self.db.query(Agent).filter(Agent.id == request.agent_id).first()
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        
        # 根据智能体type字段判断是用哪个平台的适配器
        adapter_type: str = str(agent.type)
        
        # 使用智能体的配置（config）创建适配器
        agent_config_dict = agent.config_dict
        adapter_config = dict[str, Any]()
        for key, value in agent_config_dict.items():
            adapter_config[key] = value
        
        # 确保配置中包含必要的参数
        if "api_key" not in adapter_config:
            adapter_config["api_key"] = agent.config_dict.get("api_key", "")
        
        # 创建适配器
        adapter = AdapterFactory.create_adapter(adapter_type, adapter_config)
        
        # 用于收集所有流式响应
        full_message = ""
        reasoning_events = []  # 保存所有原始的agent_thought事件数据
        formatted_thought = {}
        workflow_events = []
        other_events = []  # 保存其他事件
        conversation_id = None
        message_id = None
        
        try:
            # 执行流式聊天
            async for response in adapter.chat_stream(request):  # type: ignore
                # 收集消息内容
                if response.message:
                    full_message += response.message
                
                # 收集思考内容（agent_thought事件）
                if response.metadata and response.metadata.get("event") == "agent_thought":
                    # 将每个agent_thought事件添加到列表中，而不是覆盖
                    reasoning_events.append(response.metadata)
                    thought_data = response.metadata
                    
                    # 构建格式化的思考内容（用于后续处理）
                    thought_text = thought_data.get("thought", "")
                    
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
                    
                    # 构建formatted_thought字典（用于后续处理）
                    formatted_thought = {
                        "content": thought_text,
                        "tool_calls": [],
                        "file_references": []
                    }
                    
                    # 添加工具调用信息到formatted_thought
                    if thought_data.get("tool"):
                        formatted_thought["tool_calls"].append({
                            "name": thought_data.get("tool"),
                            "input": thought_data.get("tool_input", "")
                        })
                    
                    # 添加文件引用信息到formatted_thought
                    if thought_data.get("message_files"):
                        formatted_thought["file_references"] = thought_data.get("message_files")
                        
                # 收集工作流事件和其他事件
                elif response.metadata and "event" in response.metadata:
                    event_type = response.metadata.get("event")
                    # 收集工作流相关事件
                    if event_type and event_type != "agent_thought" and ("workflow" in event_type or "node" in event_type or event_type in ["message_end", "message_file"]):
                        workflow_events.append(response.metadata)
                    # 只收集非回复类的其他事件（避免将agent_message、text_chunk等保存到other_events中）
                    elif event_type and not event_type.startswith(('message', 'text', 'chunk')) and event_type not in ['agent_message']:
                        other_events.append(response.metadata)
                
                # 保存消息ID（优先保留第一个非None的值）
                # 会话ID应该始终使用请求中的会话ID，不需要从响应中收集
                if response.message_id and message_id is None:
                    message_id = response.message_id
                
                # 实时yield每个响应事件
                yield response
                
            # 流结束后保存对话和消息到数据库
            self._save_conversation_and_message_stream(request, full_message, reasoning_events, workflow_events, other_events, agent)
        except Exception as e:
            # 记录错误但不中断流式传输
            print(f"流式聊天处理出错: {e}")
        finally:
            # 关闭适配器连接（如果有的话）
            # BaseAdapter定义了close抽象方法，所以我们可以安全地调用它
            try:
                await adapter.close()
            except Exception as e:
                pass
    
    def _save_conversation_and_message_stream(self, request: ChatRequest, full_message: str, reasoning_events: list, workflow_events: list, other_events: list, agent):
        """保存流式对话和消息到数据库"""
        try:
            # 生成对话ID（如果有会话ID，强制使用传参的会话ID；如果没有会话ID就可以有解析出来的会话ID；如果都没有的话就新建会话ID）
            conversation_id = request.conversation_id
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # 保存或更新对话
            conversation = self.db.query(Conversation).filter(
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
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)
            elif request.conversation_id and request.conversation_id != conversation_id:
                # 更新对话的更新时间
                # 让数据库自动更新
                self.db.commit()
        
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
            self.db.add(user_message)
            
            # 保存AI回复消息（总是保存，即使内容为空）
            # 提取workflow_events（如果有的话）
            metadata_for_storage = None  # 不再存储metadata，因为信息已经提取到workflow_events中
            
            # 计算token和费用
            # 基于完整消息内容计算token数（按4字符=1token估算）
            content_length = len(full_message)
            content_tokens = max(1, content_length // 4)
            
            # 计算workflow_events的token数
            workflow_tokens = 0
            if workflow_events:
                try:
                    workflow_events_str = json.dumps(workflow_events)
                    workflow_tokens = max(1, len(workflow_events_str) // 4)
                except Exception:
                    workflow_tokens = 1
            
            # 总token数
            total_tokens = content_tokens + workflow_tokens
            
            # 计算费用（按照每百万token 12元的价格）
            cost = 0.0
            if total_tokens > 0:
                cost = (total_tokens / 1000000) * 12
            
            # 处理reasoning_events，确保保存完整的工具调用响应数据
            processed_reasoning_events = []
            if reasoning_events:
                # 创建一个字典来合并相同工具调用的不同事件
                tool_calls_dict = {}
                
                for event in reasoning_events:
                    # 检查是否是工具调用事件
                    if event.get('tool') or event.get('tool_name') or event.get('name') or event.get('toll'):
                        tool_name = event.get('tool') or event.get('tool_name') or event.get('name') or event.get('toll')
                        tool_input = event.get('tool_input') or event.get('input') or ''
                        
                        # 使用工具名和输入作为唯一键
                        tool_key = f"{tool_name}_{str(tool_input)}"
                        
                        # 如果已经有这个工具调用，合并数据
                        if tool_key in tool_calls_dict:
                            # 优先保留observation数据
                            if event.get('observation') and not tool_calls_dict[tool_key].get('observation'):
                                tool_calls_dict[tool_key]['observation'] = event['observation']
                        else:
                            # 添加新的工具调用
                            tool_calls_dict[tool_key] = event
                    else:
                        # 非工具调用事件直接添加
                        processed_reasoning_events.append(event)
                
                # 将合并后的工具调用添加到处理后的事件列表中
                processed_reasoning_events.extend(tool_calls_dict.values())
            
            ai_message = Message(
                conversation_id=conversation_id,
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                role="agent",
                content=full_message,  # 确保保存完整的流式响应内容
                reasoning_events=processed_reasoning_events if processed_reasoning_events else None,  # 保存原始的agent_thought事件数据
                other_events=other_events if other_events else None,  # 保存其他事件
                message_metadata=metadata_for_storage,
                workflow_events=workflow_events if workflow_events else None,
                cost=cost,
                total_tokens=total_tokens,
                total_tokens_estimated=total_tokens  # 使用实际计算的token数
            )
            self.db.add(ai_message)
            
            self.db.commit()
        except Exception as e:
            # 记录错误但不中断流式传输
            print(f"保存消息到数据库时出错: {e}")
            self.db.rollback()
    
    def _save_conversation_and_message(self, request: ChatRequest, response: ChatResponse, agent):
        """保存对话和消息到数据库"""
        try:
            # 生成对话ID（如果有会话ID，强制使用传参的会话ID；如果没有会话ID就可以有解析出来的会话ID；如果都没有的话就新建会话ID）
            conversation_id = request.conversation_id
            if not conversation_id:
                conversation_id = response.conversation_id or str(uuid.uuid4())
            
            # 保存或更新对话
            conversation = self.db.query(Conversation).filter(
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
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)
            elif request.conversation_id and request.conversation_id != conversation_id:
                # 更新对话的更新时间
                # 让数据库自动更新
                self.db.commit()
        
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
            self.db.add(user_message)
            
            # 保存AI回复消息（总是保存，即使内容为空）
            # 提取workflow_events（如果有的话）
            workflow_events = []
            reasoning_events = []
            other_events = []
            metadata_for_storage = response.metadata

            # 处理workflow_events和thought_content
            if response.metadata and "workflow_events" in response.metadata:
                workflow_events = response.metadata["workflow_events"]
                # 从message_metadata中移除workflow_events数据，避免重复存储
                metadata_for_storage = None
            elif response.metadata and "event" in response.metadata:
                # 在流式处理中已经正确分类事件，这里只需要确保分类正确
                event_type = response.metadata.get("event")
                # agent_thought事件应该存储在reasoning_events中
                if event_type == "agent_thought":
                    reasoning_events = [response.metadata]
                    metadata_for_storage = None
                # 工作流事件应该存储在workflow_events中
                elif event_type and event_type != "agent_thought" and not event_type.startswith(('message', 'text', 'chunk')) and ("workflow" in event_type or "node" in event_type or event_type in ["message_end", "message_file", "statistics"]):
                    workflow_events = [response.metadata]
                    metadata_for_storage = None
                # 不应该将回复类事件存储在other_events中
                elif event_type and not event_type.startswith(('message', 'text', 'chunk')) and event_type not in ['agent_message']:
                    other_events = [response.metadata]
                    metadata_for_storage = None

                elif response.metadata:
                    # 处理没有"event"字段但有metadata的情况
                    # 检查是否包含thought_content字段
                    if "thought_content" in response.metadata:
                        # 将字符串转换为字典格式
                        reasoning_events.append({"content": response.metadata.get("thought_content", "")})
                        metadata_for_storage = None
                    elif "event" in response.metadata and response.metadata["event"] == "agent_thought":
                        # 确保agent_thought事件被正确处理
                        reasoning_events.append(response.metadata)
                        metadata_for_storage = None
        
            # 计算token和费用
            # 优先使用response.total_tokens的值，如果不存在则使用total_tokens_estimated
            total_tokens = response.total_tokens if hasattr(response, 'total_tokens') and response.total_tokens is not None else response.total_tokens_estimated
            # 确保token数不为None且不为负数
            if total_tokens is None:
                # 使用基于内容和workflow_events的备用计算方法
                content_length = len(response.message or "")
                workflow_events_length = 0
                if workflow_events:
                    try:
                        workflow_events_str = json.dumps(workflow_events)
                        workflow_events_length = len(workflow_events_str)
                    except Exception:
                        workflow_events_length = 0
        
                # 计算content_tokens和workflow_tokens
                content_tokens = max(1, content_length // 4)
                workflow_tokens = max(1, workflow_events_length // 4) if workflow_events_length > 0 else 1
                total_tokens = content_tokens + workflow_tokens
            else:
                total_tokens = max(0, total_tokens)
        
            # 计算费用（按照每百万token 12元的价格）
            cost = 0.0
            if total_tokens > 0:
                cost = (total_tokens / 1000000) * 12
        
            # 处理reasoning_events，确保保存完整的工具调用响应数据
            processed_reasoning_events = []
            if reasoning_events:
                for event in reasoning_events:
                    # 确保每个agent_thought事件都保存完整的数据，包括observation
                    processed_reasoning_events.append(event)
        
            ai_message = Message(
                conversation_id=conversation_id,
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                role="agent",
                content=response.message or "",  # 确保content不为None
                reasoning_events=processed_reasoning_events if processed_reasoning_events else None,  # 保存思考内容
                other_events=other_events if other_events else None,  # 保存其他事件
                message_metadata=metadata_for_storage,
                workflow_events=workflow_events if workflow_events else None,
                cost=cost,
                total_tokens=total_tokens,
                total_tokens_estimated=response.total_tokens_estimated or total_tokens  # 确保保存估算的token数
            )
            self.db.add(ai_message)
            
            self.db.commit()
        except Exception as e:
            # 记录错误但不中断流式传输
            print(f"保存消息到数据库时出错: {e}")
            self.db.rollback()