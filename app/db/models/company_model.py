from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean


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
    registration_date = Column(DateTime, default=datetime.utcnow)
