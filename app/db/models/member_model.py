from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.base import Base


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
    registration_date = Column(DateTime, default=datetime.utcnow)
