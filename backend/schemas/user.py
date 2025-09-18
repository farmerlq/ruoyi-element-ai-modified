from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    merchant_id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password_hash: str

class UserUpdate(UserBase):
    merchant_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password_hash: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    password_hash: str

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass