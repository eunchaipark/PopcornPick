from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    """
    회원가입 요청 바디 스키마
    """
    email: EmailStr
    username: str
    password: str

class UserRegisterResponse(BaseModel):
    """
    회원가입 응답 바디 스키마
    """
    user_id: int
    email: EmailStr
    username: str
    created_at: datetime

class UserLoginRequest(BaseModel):
    """
    로그인 요청 바디 스키마
    """
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """
    로그인 성공 시 JWT 발급 응답 스키마
    """
    access_token: str
    token_type: str = "bearer"
