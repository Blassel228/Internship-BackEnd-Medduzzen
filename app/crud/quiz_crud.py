from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.quiz_model import QuizModel
from app.repositories.crud_repository import CrudRepository


class QuizCrud(CrudRepository):
    async def get_all_pagination(
        self, db: AsyncSession, limit: int = 10, offset: int = 0
    ) -> Sequence:
        result = await db.scalars(select(self.model).limit(limit).offset(offset))
        return result.all()


quiz_crud = QuizCrud(QuizModel)
