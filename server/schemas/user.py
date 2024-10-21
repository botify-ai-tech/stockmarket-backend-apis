from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    avatar: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_verified: Optional[bool] = False
    is_active: Optional[bool] = False
    disabled: Optional[bool] = False
    role: Optional[str] = "member"
    providers: Optional[str] = None
    hashed_password: Optional[str] = None
    is_social: Optional[bool] = False
    firebase_id: Optional[str] = None
    device: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RespUser(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    device: Optional[str] = None
    is_verified: Optional[bool] = None
    providers: Optional[str] = None
    role: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    token: Optional[Token]
    


class User(BaseModel):
    hashed_password: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreateInput(BaseModel):
    username: str
    email: EmailStr
    password: str
    device: str

class LoginInput(BaseModel):
    email: EmailStr
    password: str


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


class EmailSchema(BaseModel):
    email: EmailStr
    type: str


class UserProfile(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    role: Optional[str] = None


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str

class RefreshToken(BaseModel):
    refresh_toekn: str

class GoogleAuthSchema(BaseModel):
    token: str
    device: str

class DeleteUser(BaseModel):
    email: str