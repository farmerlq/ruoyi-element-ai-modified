from typing import Dict, Any, AsyncGenerator, Optional
from sqlalchemy.orm import Session
from core.adapter import AdapterFactory, ChatRequest, ChatResponse
from models.agent import Agent
from models.session import Conversation
from models.message import Message
import asyncio
import uuid

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
        adapter_type = agent.type
        
        # 使用智能体的配置（config）创建适配器
        adapter_config = agent.config_dict.copy()
        
        # 确保配置中包含必要的参数
        if "api_key" not in adapter_config:
            adapter_config["api_key"] = agent.config_dict.get("api_key", "")
        
        # 创建适配器
        adapter = AdapterFactory.create_adapter(adapter_type, adapter_config)
        
        try:
            # 根据智能体的配置（config）中的stream判断是流式还是非流式响应
            is_stream = adapter_config.get("stream", False)
            
            if is_stream:
                # 如果配置要求流式响应，但我们在这个方法中需要返回单个响应，
                # 我们需要收集所有流式响应并合并它们
                full_message = ""
                metadata_list = []
                
                async for response in adapter.chat_stream(request):
                    full_message += response.message
                    if response.metadata:
                        metadata_list.append(response.metadata)
                
                # 返回合并后的响应
                return ChatResponse(
                    message=full_message,
                    conversation_id=None,
                    message_id=None,
                    metadata={"stream_responses": metadata_list}
                )
            else:
                # 执行普通聊天
                response = await adapter.chat(request)
                
                # 保存对话和消息到数据库
                self._save_conversation_and_message(request, response, agent)
                
                return response
        finally:
            # 关闭适配器连接（如果有的话）
            if hasattr(adapter, 'close'):
                await adapter.close()
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """处理流式聊天请求"""
        # 获取agent信息
        agent = self.db.query(Agent).filter(Agent.id == request.agent_id).first()
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_id}")
        
        # 根据智能体type字段判断是用哪个平台的适配器
        adapter_type = agent.type
        
        # 使用智能体的配置（config）创建适配器
        adapter_config = agent.config_dict.copy()
        
        # 确保配置中包含必要的参数
        if "api_key" not in adapter_config:
            adapter_config["api_key"] = agent.config_dict.get("api_key", "")
        
        # 创建适配器
        adapter = AdapterFactory.create_adapter(adapter_type, adapter_config)
        
        # 用于收集所有流式响应
        full_message = ""
        workflow_events = []
        conversation_id = None
        message_id = None
        
        try:
            # 执行流式聊天
            async for response in adapter.chat_stream(request):
                yield response
                
                # 收集消息内容
                if response.message:
                    full_message += response.message
                
                # 收集工作流事件
                if response.metadata and "event" in response.metadata:
                    workflow_events.append(response.metadata)
                
                # 保存对话ID和消息ID
                if response.conversation_id:
                    conversation_id = response.conversation_id
                if response.message_id:
                    message_id = response.message_id
        finally:
            # 关闭适配器连接（如果有的话）
            if hasattr(adapter, 'close'):
                await adapter.close()
            
            # 在所有流式响应完成后，保存完整的消息到数据库
            if full_message or workflow_events:
                # 创建最终的ChatResponse
                final_response = ChatResponse(
                    message=full_message,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    metadata={"workflow_events": workflow_events} if workflow_events else None
                )
                # 保存对话和消息到数据库
                self._save_conversation_and_message(request, final_response, agent)
    
    def _save_conversation_and_message(self, request: ChatRequest, response: ChatResponse, agent):
        """保存对话和消息到数据库"""
        try:
            # 生成对话ID（如果不存在）
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
                    title=request.query[:100],  # 使用前100个字符作为标题
                    status="active"
                )
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)
            elif request.conversation_id != conversation_id:
                # 更新对话的更新时间
                conversation.updated_at = None  # 让数据库自动更新
                self.db.commit()
        
            # 保存用户消息
            user_message = Message(
                conversation_id=conversation_id,
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                agent_id=request.agent_id,
                role="user",
                content=request.query
            )
            self.db.add(user_message)
            
            # 保存AI回复消息
            if response.message or (response.metadata and "workflow_events" in response.metadata):
                # 提取workflow_events（如果有的话）
                workflow_events = []
                metadata_for_storage = response.metadata
                
                # 处理workflow_events
                if response.metadata and "workflow_events" in response.metadata:
                    workflow_events = response.metadata["workflow_events"]
                    # 从message_metadata中移除workflow_events数据，避免重复存储
                    metadata_for_storage = None
                elif response.metadata and "event" in response.metadata:
                    # 如果是单个工作流事件，保存到workflow_events字段
                    workflow_events = [response.metadata]
                    # 从message_metadata中移除工作流事件数据，避免重复存储
                    metadata_for_storage = None
                
                ai_message = Message(
                    conversation_id=conversation_id,
                    merchant_id=request.merchant_id,
                    user_id=request.user_id,
                    agent_id=request.agent_id,
                    role="agent",
                    content=response.message or "",  # 确保content不为None
                    message_metadata=metadata_for_storage,
                    workflow_events=workflow_events
                )
                self.db.add(ai_message)
            
            self.db.commit()
        except Exception as e:
            # 记录错误但不中断流式传输
            print(f"保存消息到数据库时出错: {e}")
            self.db.rollback()