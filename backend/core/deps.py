from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from core.security import get_current_user, oauth2_scheme
from core.config import settings
from models.user import User

def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme) if settings.ENABLE_AUTH else None
) -> Optional[User]:
    """
    获取当前用户，如果认证未启用或未登录则返回None
    """
    if not settings.ENABLE_AUTH:
        return None
    try:
        return get_current_user(token, db)
    except:
        return None

def get_current_user_or_raise(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme) if settings.ENABLE_AUTH else None
) -> User:
    """
    获取当前用户，如果认证未启用则返回None，如果启用但未认证则抛出异常
    """
    # 认证未启用时，返回None
    if not settings.ENABLE_AUTH:
        # 创建一个默认用户对象
        from models.user import User
        default_user = User(
            id=0,
            username="default",
            merchant_id=0
        )
        return default_user
    
    try:
        user = get_current_user(token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
def get_current_merchant_id(
    current_user: User = Depends(get_current_user_or_raise)
):
    """
    获取当前商户ID
    """
    if not settings.ENABLE_AUTH:
        return None
    
    if current_user:
        return current_user.merchant_id
    return None