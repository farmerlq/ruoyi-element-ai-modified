from pydantic import BaseModel, ConfigDict
from typing import Optional

class Token(BaseModel):
    model_config = ConfigDict()
    
    access_token: str
    token_type: str

class TokenData(BaseModel):
    model_config = ConfigDict()
    
    username: Optional[str] = None

class LoginRequest(BaseModel):
    model_config = ConfigDict()
    
    username: str
    password: str