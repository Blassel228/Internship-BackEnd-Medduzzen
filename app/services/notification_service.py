import datetime
from app.CRUD.notification_crud import notification_crud
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud
from app.CRUD.quiz_crud import quiz_crud
from app.CRUD.quiz_result_crud import quiz_result_crud
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import NotificationCreateSchema
from fastapi import HTTPException


class NotificationService:
    async def notify_users(
        self, quiz_id: int, company_id: int, notification_text: str, db: AsyncSession
    ):
        company = await company_crud.get_one(id_=company_id, db=db)
        for member in company.members:
            if member.company_id == company.id:
                notification = NotificationCreateSchema(
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

    async def pass_check(self, text: str, db: AsyncSession):
        members = await member_crud.get_all(db=db)
        quizzes = await quiz_crud.get_all(db=db)
        time_difference = datetime.timedelta()
        notifications = list()
        for quiz in quizzes:
            for member in members:
                passed_quizzes = await quiz_result_crud.get_all_by_filter(
                    filters={"quiz_id": quiz.id, "user_id": member.id}, db=db
                )
                if passed_quizzes:
                    latest = passed_quizzes[0]
                    for passed_quiz in passed_quizzes:
                        if latest.registration_date < passed_quiz.registration_date:
                            latest = passed_quiz

                    time_difference = (
                        datetime.datetime.utcnow() - latest.registration_date
                    )

                if (
                    time_difference > datetime.timedelta(minutes=1)
                    or not passed_quizzes
                ):
                    notification = NotificationCreateSchema(
                        quiz_id=quiz.id, user_id=member.id, text=text
                    )
                    await notification_crud.add(data=notification, db=db)
                    await db.commit()
                    notifications.append(notification.model_dump())

        return notifications


notification_service = NotificationService()
