from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    userInfo: Optional[dict] = None

class TokenData(BaseModel):
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import authenticate_user, create_access_token, get_current_user, get_token_payload, ACCESS_TOKEN_EXPIRE_MINUTES
from core.config import settings
from schemas.user import User as UserSchema
from schemas.auth import Token, LoginRequest
from models.user import User

router = APIRouter(tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login_for_access_token(
    login_request: LoginRequest, 
    db: Session = Depends(get_db)
):
    """
    用户登录并获取访问令牌
    """
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建包含用户信息和商户ID的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": user.username,
        "merchant_id": user.merchant_id,
        "user_id": user.id,
        "role": user.role
    }
    
    access_token = create_access_token(
        data=access_token_data, expires_delta=access_token_expires
    )
    
    # 将数据库模型转换为字典格式的用户信息
    user_info = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "merchant_id": user.merchant_id,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "userInfo": user_info
    }

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user

@router.get("/verify")
async def verify_token(
    token_payload: dict = Depends(get_token_payload)
):
    """
    验证令牌
    """
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_payload