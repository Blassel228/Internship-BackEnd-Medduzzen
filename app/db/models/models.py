from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_async_engine(settings.postgres_url)
session = async_sessionmaker(engine, expire_on_commit=False)


class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    registration_date = Column(DateTime, default=datetime.now())


class CompanyModel(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    owner_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    visible = Column(Boolean, default=True)
    members = relationship("MemberModel", backref="company", lazy="selectin")
    registration_date = Column(String, default=str(datetime.now()))


class InvitationModel(Base):
    __tablename__ = "invitation"
    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    recipient_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    invitation_text = Column(String)
    registration_date = Column(String, default=str(datetime.now()))


class MemberModel(Base):
    __tablename__ = "member"
    id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    company_id = Column(
        Integer,
        ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String, nullable=False, default="member")
    registration_date = Column(String, default=str(datetime.now()))


class RequestModel(Base):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    sender_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    request_text = Column(String)
    registration_date = Column(String, default=str(datetime.now()))


class QuizModel(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer, ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    questions = relationship(
        "QuestionModel",
        back_populates="quizzes",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pass_count = Column(Integer, default=0)
    registration_date = Column(String, default=str(datetime.now()))


class QuestionModel(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    quiz_id = Column(
        Integer,
        ForeignKey("quiz.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    options = relationship(
        "OptionModel", back_populates="question", cascade="all, delete-orphan"
    )
    quizzes = relationship("QuizModel", back_populates="questions")


class OptionModel(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    question_id = Column(
        Integer,
        ForeignKey("question.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    question = relationship("QuestionModel", back_populates="options")


class QuizResultModel(Base):
    __tablename__ = "quiz_result"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    company_id = Column(
        Integer,
        ForeignKey("company.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    quiz_id = Column(
        Integer,
        ForeignKey("quiz.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    score = Column(Float, nullable=False)
    user = relationship("UserModel", backref="quiz_results")
    company = relationship("CompanyModel", backref="quiz_results")
    quiz = relationship("QuizModel", backref="quiz_results")
    registration_date = Column(String, default=str(datetime.now()))
