from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.crud_repository import CrudRepository
from app.db.models.models import NotificationModel


class NotificationCrud(CrudRepository):
    async def add(self, data: BaseModel, db: AsyncSession):
        stmt = insert(self.model).values(**data.model_dump())
        res = await db.execute(stmt)
        if res.rowcount == 0:
            return None
        return res


notification_crud = NotificationCrud(NotificationModel)
