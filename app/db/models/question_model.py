from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


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
        "OptionModel",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quizzes = relationship("QuizModel", back_populates="questions")
