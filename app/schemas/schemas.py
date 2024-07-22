from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


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
    owner_id: int


class CompanyCreateInSchema(BaseModel):
    id: int
    name: str
    description: str
    visible: bool


class CompanyUpdateSchema(BaseModel):
    name: str
    description: str


class CompanyUpdateVisibility(BaseModel):
    visible: bool


class InvitationCreateSchema(BaseModel):
    id: int
    company_id: int
    recipient_id: int
    invitation_text: str


class MemberCreateSchema(BaseModel):
    id: int
    company_id: int


class RequestCreateInSchema(BaseModel):
    id: int
    company_id: int
    request_text: str


class RequestCreateSchema(BaseModel):
    id: int
    company_id: int
    sender_id: int
    request_text: str


class OptionCreateSchema(BaseModel):
    text: str
    is_correct: bool


class QuestionCreateSchema(BaseModel):
    text: str
    options: List[OptionCreateSchema]


class QuizCreateSchema(BaseModel):
    id: int
    name: str
    description: str
    questions: List[QuestionCreateSchema]


class QuizResultCreateInSchema(BaseModel):
    id: int
    quiz_id: int
    options_ids: list


class QuizResultCreateSchema(BaseModel):
    id: int
    quiz_id: int
    company_id: int
    score: float
    user_id: int


class QuizResultUpdateSchema(BaseModel):
    score: float
    registration_date: str
