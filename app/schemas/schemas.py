from pydantic import BaseModel, EmailStr
from typing import List

class UserCreateSchema(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr

class UserUpdateInSchema(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr

class UserUpdateSchema(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: EmailStr