from pydantic import BaseModel, EmailStr

from datetime import datetime
from typing import Optional


class UserRequestModel(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str


class UserResponseModel(BaseModel):
    id: str
    email: EmailStr
    username: str
    created_at: Optional[datetime] = None
