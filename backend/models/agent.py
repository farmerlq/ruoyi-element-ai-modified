from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from core.database import Base
from datetime import datetime
import json

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum("dify", "n8n", "coze", "custom"), nullable=False)
    config = Column(JSON, nullable=False)
    status = Column(Enum("active", "inactive"), nullable=False, default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @property
    def config_dict(self):
        """确保配置始终返回字典"""
        if isinstance(self.config, str):
            try:
                return json.loads(self.config)
            except:
                return {}
        return self.config or {}