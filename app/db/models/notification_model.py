from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, DateTime
from sqlalchemy.orm import relationship


class NotificationModel(Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    quiz_id = Column(
        Integer,
        ForeignKey("quiz.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    is_read = Column(Boolean, nullable=False, default=False)
    text = Column(String, nullable=False)
    user = relationship("UserModel", backref="notifications")
    quiz = relationship("QuizModel", backref="notifications")
    registration_date = Column(DateTime, default=datetime.utcnow)
