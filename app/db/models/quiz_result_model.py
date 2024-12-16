from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship


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
    registration_date = Column(DateTime, default=datetime.utcnow)
