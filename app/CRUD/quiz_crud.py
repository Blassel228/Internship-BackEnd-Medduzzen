from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.crud_repository import CrudRepository
from app.db.models.models import QuizModel


class QuizCrud(CrudRepository):
    async def get_quizzes(self, db: AsyncSession, limit: int = 10, offset: int = 0):
        async with db.begin():
            result = await db.execute(select(QuizModel).limit(limit).offset(offset))
            quizzes = result.scalars().all()
            return quizzes


quiz_crud = QuizCrud(QuizModel)
