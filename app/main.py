import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.routers.token_router import token_router
from logging_config import LOGGING_CONFIG
from app.routers.user_router import user_router
from app.routers.db_check_router import db_check_router
import logging

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(db_check_router)
app.include_router(user_router)
app.include_router(token_router)


@app.get("/")
def read_root():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@app.get("/health_check")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "healthy"}



if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.uvicorn_host, port=settings.uvicorn_port, reload=True
    )
