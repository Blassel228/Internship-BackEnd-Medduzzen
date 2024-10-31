from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.base import Base


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
    registration_date = Column(DateTime, default=datetime.utcnow)
