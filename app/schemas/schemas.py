from pydantic import BaseModel, EmailStr
from typing import Optional


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
    id: Optional[int] = None
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    email: Optional[EmailStr] = None


class UserSelfUpdateSchema(BaseModel):
    username: str
    hashed_password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class CompanyCreateSchema(BaseModel):
    id: int
    name: str
    description: str
    visible: bool


class CompanyCreateInSchema(BaseModel):
    id: int
    name: str
    description: str
    visible: bool
    owner_id: int


class CompanyUpdateSchema(BaseModel):
    name: str
    description: str


class CompanyUpdateVisibility(BaseModel):
    visible: bool
