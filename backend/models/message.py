from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float
from sqlalchemy.dialects.mysql import JSON
from core.database import Base
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, cast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.types import TypeEngine

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    role = Column(Enum("user", "agent"), nullable=False)
    content = Column(Text, nullable=False)
    thought_content: Union[Column[Optional[Union[Dict[str, Any], str]]], Optional[Union[Dict[str, Any], str]]] = Column(JSON, nullable=True)  # AI思考过程(JSON格式或字符串)
    message_metadata: Union[Column[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]] = Column(JSON)
    cost = Column(Float, default=0.0, comment="消息费用")
    total_tokens = Column(Integer, default=0, comment="总token数")
    total_tokens_estimated = Column(Integer, default=0, comment="估算的总token数")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    workflow_events: Union[Column[Optional[List[Dict[str, Any]]]], Optional[List[Dict[str, Any]]]] = Column(JSON)
    
    def get_workflow_events(self) -> Optional[List[Dict[str, Any]]]:
        """获取工作流事件列表，确保返回正确的类型"""
        if self.workflow_events is None:
            return None
        return cast(List[Dict[str, Any]], self.workflow_events)