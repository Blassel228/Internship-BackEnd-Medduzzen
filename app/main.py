import uvicorn
from fastapi import FastAPI
from app.core.config import settings
import logging
from logging_config import LOGGING_CONFIG
from app.routers.user_router import user_router

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(user_router)


@app.get("/")
def read_root():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@app.get("/health_check")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "healthy"}


@app.get("/error")
async def trigger_error():
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception("An error occurred: %s", e)
        raise e


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.uvicorn_host, port=settings.uvicorn_port, reload=True
    )
