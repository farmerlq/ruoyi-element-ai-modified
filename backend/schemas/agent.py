from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AgentBase(BaseModel):
    merchant_id: int
    name: str
    description: Optional[str] = None
    type: str
    config: Dict[str, Any]
    status: Optional[str] = "active"
    created_by: int

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    merchant_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    created_by: Optional[int] = None

class AgentInDBBase(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Agent(AgentInDBBase):
    pass