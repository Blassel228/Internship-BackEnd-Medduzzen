from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO)

metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_async_engine(f'postgresql+asyncpg://{settings.postgresql_user}:{settings.postgresql_password}@{settings.postgresql_host}:{settings.postgresql_port}/{settings.postgresql_database_name}')
session = async_sessionmaker(engine, expire_on_commit=False)

class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    registration_date = Column(DateTime, default=datetime.now())