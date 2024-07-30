from app.core.config import settings
import redis.asyncio as redis


async def redis_connect():
    redis_conn = await redis.Redis(
        host=settings.redis_host, port=settings.redis_port
    )
    return redis_conn
