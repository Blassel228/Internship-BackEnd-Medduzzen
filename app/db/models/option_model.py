from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


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
