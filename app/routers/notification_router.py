from app.utils.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.CRUD.notification_crud import notification_crud
from app.services.notification_service import notification_service
from app.utils.deps import get_current_user

notification_router = APIRouter(tags=["Notification"], prefix="/notification")


@notification_router.get("/get_all")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await notification_crud.get_all(db=db)


@notification_router.get("/self_get_notifications")
async def self_get_notifications(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await notification_crud.get_all_by_filter(
        filters={"user_id": current_user.id}, db=db
    )


@notification_router.put("/mark_as_read")
async def mark_as_read(
    id_: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await notification_service.mark_as_read(
        id_=id_, user_id=current_user.id, db=db
    )
