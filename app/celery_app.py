from celery import Celery
from app.core.config import settings
from celery.schedules import crontab
from app.services.notification_service import notification_service
from app.db.base import session
import asyncio

app = Celery(
    "celery_app.py",
    broker=f"redis://@{settings.redis_host}:{settings.redis_port}/0",
    backend=f"redis://@{settings.redis_host}:{settings.redis_port}/0",
)

app.conf.timezone = "Europe/Kiev"
app.conf.enable_utc = False
app.conf.broker_connection_retry_on_startup = True
app.conf.beat_schedule = {
    "task-at-midnight": {
        "task": "app.celery_app.pass_check_task",
        "schedule": crontab(minute=0, hour=0),
    }
}


@app.task
def pass_check_task():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(execute_pass_check())


async def execute_pass_check():
    async with session() as async_session:
        text = "Pass a new quiz please"
        result = await notification_service.pass_check(db=async_session, text=text)
        return result
