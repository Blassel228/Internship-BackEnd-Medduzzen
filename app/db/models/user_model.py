from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base


class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
