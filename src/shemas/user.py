from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(..., unique=True)
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: str
    avatar: Optional[str]

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


