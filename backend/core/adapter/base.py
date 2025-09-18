from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    """聊天请求基类"""
    query: str
    conversation_id: Optional[str] = None
    user_id: int
    merchant_id: int
    agent_id: int
    stream: bool = False
    extra_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应基类"""
    message: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

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