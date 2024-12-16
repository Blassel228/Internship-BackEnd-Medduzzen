import redis.asyncio as redis
import logging
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_async_engine(settings.postgres_url)
session = async_sessionmaker(engine, expire_on_commit=False)


def redis_connect():
    redis_conn = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    return redis_conn
