import logging
import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.routers.company_router import company_router
from app.routers.invitation_router import invitation_router
from app.routers.member_router import member_router
from app.routers.notification_router import notification_router
from app.routers.option_router import option_router
from app.routers.quiz_result_router import quiz_result_router
from app.routers.quiz_router import quiz_router
from app.routers.redis_router import redis_router
from app.routers.request_router import request_router
from app.routers.token_router import token_router
from app.routers.user_router import user_router
from app.routers.health_check_router import health_check_router
from app.routers.db_check_router import db_check_router
from logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(db_check_router)
app.include_router(health_check_router)
app.include_router(user_router)
app.include_router(token_router)
app.include_router(company_router)
app.include_router(invitation_router)
app.include_router(request_router)
app.include_router(member_router)
app.include_router(quiz_router)
app.include_router(option_router)
app.include_router(quiz_result_router)
app.include_router(redis_router)
app.include_router(notification_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.uvicorn_host, port=settings.uvicorn_port, reload=True
    )
