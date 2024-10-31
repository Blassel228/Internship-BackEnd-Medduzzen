import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.db.base import redis_connect
from app.db.base import engine

db_check_router = APIRouter(tags=["db_check"], prefix="/db_check")


@db_check_router.get("/redis_check")
async def redis_check():
    try:
        redis = await redis_connect()
        await redis.ping()
        return JSONResponse(content={"status": "Redis is up"}, status_code=200)
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"status": "Redis check failed", "error": str(e)}, status_code=500
        )


@db_check_router.get("/postgres_check")
async def postgres_check():
    try:
        await engine.connect()
        logging.info("Connection opened successfully.")
        return JSONResponse(content={"status": "Postgres is up"}, status_code=200)
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"status": "Postgres check failed", "error": str(e)},
            status_code=500,
        )
