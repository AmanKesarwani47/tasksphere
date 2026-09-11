from pydantic import BaseModel, Field, EmailStr

class CurrentUserResponse(BaseModel):
    user_name: str

class UserCreate(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=50, example="amank")
    email: EmailStr = Field(..., example="aman@example.com")
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True