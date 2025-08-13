from pydantic import BaseModel, EmailStr
from typing import List, Optional

# User Schemas

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# Content Schemas

class ContentBase(BaseModel):
    title: str
    body: str

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str]
    body: Optional[str]

class ContentResponse(ContentBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
