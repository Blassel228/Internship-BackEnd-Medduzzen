from typing import Optional
from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.notification_model import NotificationModel
from app.repositories.crud_repository import CrudRepository
from sqlalchemy import CursorResult


class NotificationCrud(CrudRepository):
    async def add(self, data: BaseModel, db: AsyncSession) -> Optional[CursorResult]:
        stmt = insert(self.model).values(**data.model_dump())
        res = await db.execute(stmt)
        if res.rowcount == 0:
            return None
        return res


notification_crud = NotificationCrud(NotificationModel)
