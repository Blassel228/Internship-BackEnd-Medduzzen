from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.crud_repository import CrudRepository
from app.db.models.models import QuizModel


class QuizCrud(CrudRepository):
    async def get_all_pagination(self, db: AsyncSession, limit: int = 10, offset: int = 0):
        result = await db.scalars(select(self.model).limit(limit).offset(offset))
        return result.all()


quiz_crud = QuizCrud(QuizModel)
