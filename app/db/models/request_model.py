from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime


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
    registration_date = Column(DateTime, default=datetime.utcnow)
