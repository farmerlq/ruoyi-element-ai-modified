from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Enum, Text
from core.database import Base
from datetime import datetime

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    api_key = Column(String(100), unique=True, nullable=False)
    balance = Column(DECIMAL(18, 2), default=0.00, nullable=False)
    status = Column(Enum("active", "inactive", "suspended"), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)