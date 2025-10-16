from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class MessageBase(BaseModel):
    conversation_id: str
    merchant_id: int
    user_id: int
    agent_id: int
    role: str
    content: str
    reasoning_events: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None  # AI思考过程(JSON格式或字符串)
    message_metadata: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None
    total_tokens: Optional[int] = None
    total_tokens_estimated: Optional[int] = None

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    conversation_id: Optional[str] = None
    merchant_id: Optional[int] = None
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    role: Optional[str] = None
    content: Optional[str] = None
    reasoning_events: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None
    message_metadata: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None
    total_tokens: Optional[int] = None
    total_tokens_estimated: Optional[int] = None

class Message(MessageBase):
    id: int
    created_at: datetime
    workflow_events: Optional[List[Dict[str, Any]]] = None
    other_events: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None

    model_config = ConfigDict(from_attributes=True)