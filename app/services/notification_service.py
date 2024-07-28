from app.CRUD.notification_crud import notification_crud
from app.CRUD.company_crud import company_crud
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import NotificationCreate
from fastapi import HTTPException


class NotificationService:
    async def notify_users(
        self, quiz_id: int, company_id: int, notification_text: str, db: AsyncSession
    ):
        company = await company_crud.get_one(id_=company_id, db=db)
        for member in company.members:
            if member.company_id == company.id:
                notification = NotificationCreate(
                    user_id=member.id, quiz_id=quiz_id, text=notification_text
                )
                await notification_crud.add(data=notification, db=db)

    async def mark_as_read(self, id_: int, user_id: int, db: AsyncSession):
        notification = await notification_crud.get_one(id_=id_, db=db)
        if notification is None:
            raise HTTPException(status_code=404, detail="Was not found")
        if notification.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="The notification was not sent to you"
            )
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification


notification_service = NotificationService()
