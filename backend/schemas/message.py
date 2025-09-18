from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

class MessageBase(BaseModel):
    conversation_id: str
    merchant_id: int
    user_id: int
    agent_id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None
    cost: Optional[float] = 0.0
    workflow_events: Optional[List[Dict[str, Any]]] = None

    @field_validator('cost', mode='before')
    @classmethod
    def convert_decimal_to_float(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v

class MessageCreate(MessageBase):
    pass

class MessageUpdate(MessageBase):
    conversation_id: Optional[str] = None
    merchant_id: Optional[int] = None
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    role: Optional[str] = None
    content: Optional[str] = None
    message_metadata: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None
    workflow_events: Optional[List[Dict[str, Any]]] = None

class MessageInDBBase(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Message(MessageInDBBase):
    pass