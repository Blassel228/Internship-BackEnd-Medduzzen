from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship


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
        lazy="selectin"
    )
    pass_count = Column(Integer, default=0)
    registration_date = Column(DateTime, default=datetime.utcnow)
