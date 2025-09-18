from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MerchantBase(BaseModel):
    name: str
    description: Optional[str] = None
    api_key: str
    balance: Optional[float] = 0.00
    status: Optional[str] = "active"

class MerchantCreate(MerchantBase):
    pass

class MerchantUpdate(MerchantBase):
    name: Optional[str] = None
    api_key: Optional[str] = None
    balance: Optional[float] = None
    status: Optional[str] = None

class MerchantInDBBase(MerchantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Merchant(MerchantInDBBase):
    pass