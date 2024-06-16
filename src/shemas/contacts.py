from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

from src.shemas.user import UserResponse


class ContactSchema(BaseModel):
    name: str = Field(max_length=50)
    surname: str = Field(max_length=100)
    email: EmailStr = Field(..., unique=True)
    phone: str = Field(max_length=15)
    birthday: datetime
    description: Optional[str] = None


class ContactUpdateSchema(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[datetime] = None
    description: Optional[str] = None


class ContactSearchSchema(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: str
    phone: str
    birthday: datetime
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True
