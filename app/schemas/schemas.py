from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr


class UserUpdateSchema(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenBearerSchema(BaseModel):
    sub: str = None
    email: str = None
