# models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class RoleModel(BaseModel):
    """Role Model"""

    name: str = Field(min_length=3, max_length=50)
    permissions: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


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
        allow_population_by_field_name = True  # Allow using alias names like _id


# class DjangoUserWrapper:
#     def __init__(self, user_model):
#         self._user_model = user_model

#     @property
#     def id(self):
#         return self._user_model._id

#     @property
#     def email(self):
#         return self._user_model.email

#     @property
#     def is_active(self):
#         return self._user_model.is_active

#     @property
#     def role(self):
#         return self._user_model.role
