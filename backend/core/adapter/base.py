from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, Optional, List
from pydantic import BaseModel, Field, validator, root_validator

class Message(BaseModel):
    """OpenAI格式的消息"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """聊天请求基类 - 支持两种格式"""
    # 简单格式
    query: Optional[str] = None
    
    # OpenAI格式
    messages: Optional[List[Message]] = None
    
    conversation_id: Optional[str] = None
    user_id: int
    merchant_id: int
    agent_id: int
    extra_data: Optional[Dict[str, Any]] = None

    @root_validator(pre=True)
    def validate_query_or_messages(cls, values):
        """确保至少提供query或messages中的一个"""
        query = values.get('query')
        messages = values.get('messages')
        
        if query is None and messages is None:
            raise ValueError('必须提供query或messages中的一个')
        if query is not None and not query.strip():
            raise ValueError('query不能为空字符串')
        if messages is not None and len(messages) == 0:
            raise ValueError('messages不能为空数组')
            
        return values

    def get_query_text(self) -> str:
        """获取查询文本，优先使用query字段，如果没有则从messages中提取"""
        if self.query:
            return self.query
        
        if self.messages:
            # 提取最后一条用户消息
            for message in reversed(self.messages):
                if message.role == 'user':
                    return message.content
            
            # 如果没有用户消息，返回最后一条消息的内容
            if self.messages:
                return self.messages[-1].content
        
        return ""

class ChatResponse(BaseModel):
    """聊天响应基类"""
    message: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    total_tokens: Optional[int] = None  # 添加：实际总token数
    total_tokens_estimated: Optional[int] = None  # 新增：估算的总token数
    estimated_cost: Optional[float] = None       # 新增：估算的费用

class BaseAdapter(ABC):
    """平台适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理普通聊天请求"""
        pass
    
    @abstractmethod
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """处理流式聊天请求"""
        pass
    
    @abstractmethod
    async def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        """获取对话历史"""
        pass
    
    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        pass
    
    @abstractmethod
    async def close(self):
        """关闭适配器连接"""
        pass