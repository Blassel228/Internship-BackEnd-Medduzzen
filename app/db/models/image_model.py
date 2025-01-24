from datetime import datetime
from sqlalchemy import ForeignKey, Integer, Column, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class ImageModel(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    file_name = Column(String, nullable=False)
    image_data = Column(LargeBinary, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserModel", back_populates="image", uselist=False)

