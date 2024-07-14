from pydantic import BaseModel, EmailStr
from typing import List

class UserSchema(BaseModel): #UserDetail
    id: int
    username: str
    password: str
    email: EmailStr

class SignUpSchema(BaseModel):
    username: str
    password: str
    email: EmailStr

class SignInSchema(BaseModel):
    username: str
    password: str

class UserUpdateRequestSchema(BaseModel):
    username: str
    password: str

class UsersListSchema(BaseModel):
    users: List[UserSchema]