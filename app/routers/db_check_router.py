from app.db.base import redis_connect, engine
from fastapi import APIRouter
import logging

db_check_router = APIRouter(tags=["db_check"], prefix="/db_check")


@db_check_router.get("/redis_check")
async def redis_check():
    try:
        redis = await redis_connect()
        return await redis.ping()
    except Exception as e:
        logging.error(e)
        return False


@db_check_router.get("/postgres_check")
async def postgres_check():
    try:
        await engine.connect()
        logging.info("Connection opened successfully.")
        return True
    except Exception as e:
        logging.error(e)
        return False
