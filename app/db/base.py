from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import redis.asyncio as redis

metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_async_engine(settings.postgres_url)
session = async_sessionmaker(engine, expire_on_commit=False)


async def redis_connect():
    redis_conn = await redis.Redis(host=settings.redis_host, port=settings.redis_port)
    return redis_conn
