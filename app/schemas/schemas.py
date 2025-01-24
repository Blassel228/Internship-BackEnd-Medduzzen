from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserGetSchema(BaseModel):
    username: str
    email: EmailStr


class UserCreateSchema(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    email: EmailStr


class UserUpdateInSchema(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None


class UserUpdateSchema(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    email: Optional[EmailStr] = None


class UserSelfUpdateSchema(BaseModel):
    username: Optional[str] = None
    hashed_password: Optional[str] = None


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class CompanyCreateSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    visible: bool
    owner_id: int


class CompanyCreateInSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    visible: bool


class CompanyUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CompanyUpdateVisibility(BaseModel):
    visible: bool


class InvitationGetSchema(BaseModel):
    company_id: int
    recipient_id: int
    invitation_text: str


class InvitationCreateSchema(BaseModel):
    id: Optional[int] = None
    company_id: int
    recipient_id: int
    invitation_text: str


class MemberCreateSchema(BaseModel):
    id: int
    company_id: int


class RequestCreateInSchema(BaseModel):
    id: Optional[int] = None
    company_id: int
    request_text: str


class RequestCreateSchema(BaseModel):
    id: Optional[int] = None
    company_id: int
    sender_id: int
    request_text: str


class RequestGetSchema(BaseModel):
    company_id: int
    sender_id: int
    request_text: str


class OptionCreateSchema(BaseModel):
    text: str
    is_correct: bool


class OptionUpdateSchema(BaseModel):
    str: str
    is_correct: bool


class OptionGetSchema(BaseModel):
    text: str
    is_correct: bool

    class Config:
        extra = "allow"


class QuestionCreateSchema(BaseModel):
    text: str
    options: List[OptionCreateSchema]


class QuestionUpdateSchema(BaseModel):
    text: str
    quiz_id: int


class QuestionGetSchema(BaseModel):
    text: str
    options: List[OptionGetSchema]

    class Config:
        extra = "allow"


class QuizCreateSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    questions: Optional[List[QuestionCreateSchema]] = None


class QuizGetSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    questions: Optional[List[QuestionGetSchema]] = None

    class Config:
        extra = "allow"


class QuizResultCreateInSchema(BaseModel):
    id: int
    quiz_id: int
    options_ids: list[int]


class QuizResultCreateSchema(BaseModel):
    id: int
    quiz_id: int
    company_id: int
    score: float
    user_id: int


class QuizResultUpdateSchema(BaseModel):
    score: float
    registration_date: str


class NotificationCreateSchema(BaseModel):
    user_id: int
    quiz_id: int
    text: str


class LoginData(BaseModel):
    username: str
    password: str


class CreateImage(BaseModel):
    user_id: int
    file_name: str
    image_data: bytes


class ImageResponseByte(BaseModel):
    file_name: str
    image_data: Optional[bytes] = None

    class Config:
        from_attributes = True
        exclude_none = True


class ImageResponse(BaseModel):
    file_name: str
    image_data: Optional[str] = None

    class Config:
        from_attributes = True
        exclude_none = True
