from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, DECIMAL
from sqlalchemy.dialects.mysql import JSON
from core.database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    role = Column(Enum("user", "agent"), nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON)
    cost = Column(DECIMAL(18, 6), default=0.000000, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    workflow_events = Column(JSON)