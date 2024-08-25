# models.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    """User model"""

    id: Optional[str] = Field(None, alias="_id")  # Using alias to handle MongoDB's _id
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    is_active: bool = True
    role: Optional[str] = None

    @property
    def is_authenticated(self):
        return True

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True


class UserActivityModel(BaseModel):
    user_email: str
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str
    details: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
