from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.CRUD.notification_crud import notification_crud
from app.services.notification_service import notification_service
from app.utils.deps import get_db, get_current_user

notification_router = APIRouter(tags=["Notification"], prefix="/notifications")


@notification_router.get("/user/all")
async def get_user_all(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """"Get notifications for current user"""
    return await notification_crud.get_all_by_filter(
        filters={"user_id": current_user.id}, db=db
    )


@notification_router.get("/")
async def get_all_notifications(db: AsyncSession = Depends(get_db)):
    return await notification_crud.get_all(db=db)


@notification_router.get("/user/{user_id}")
async def get_user_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    return await notification_crud.get_all_by_filter(
        filters={"user_id": user_id}, db=db
    )


@notification_router.put("/{notification_id}/mark-as-read")
async def mark_notification_as_read(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.mark_as_read(
        id_=notification_id, user_id=current_user.id, db=db
    )


@notification_router.post("/check")
async def check_notification_text(text: str, db: AsyncSession = Depends(get_db)):
    return await notification_service.pass_check(text=text, db=db)
