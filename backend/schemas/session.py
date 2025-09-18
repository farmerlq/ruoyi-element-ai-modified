from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConversationBase(BaseModel):
    id: str
    merchant_id: int
    user_id: int
    agent_id: int
    title: str
    status: str
    ended_at: Optional[datetime] = None

class ConversationCreate(BaseModel):
    merchant_id: int
    user_id: int
    agent_id: int
    title: str
    status: str
    ended_at: Optional[datetime] = None

class ConversationUpdate(ConversationBase):
    merchant_id: Optional[int] = None
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    ended_at: Optional[datetime] = None

class ConversationInDBBase(ConversationBase):
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: Optional[int] = 0  # 添加消息条数字段

    class Config:
        from_attributes = True

class Conversation(ConversationInDBBase):
    pass