from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.users import UserResponse

class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        example="Buy groceries"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        example="Milk, eggs, and bread"
    )
    priority: str = Field(
        default="low",
        example="high"
    )

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    priority: str

    owner_id: int
    owner: UserResponse