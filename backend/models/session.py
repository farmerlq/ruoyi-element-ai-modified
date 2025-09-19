from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from core.database import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    status = Column(Enum("active", "ended"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime)