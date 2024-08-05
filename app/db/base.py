import redis.asyncio as redis

from app.core.config import settings


def redis_connect():
    redis_conn = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    return redis_conn
