
from typing import List
from pydantic import BaseModel, Field


class RoleModel(BaseModel):
    """Role Model"""

    name: str = Field(min_length=3, max_length=50)
    permissions: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
