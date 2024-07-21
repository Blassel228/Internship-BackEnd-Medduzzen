from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.crud_repository import CrudRepository
from app.db.models.models import MemberModel
from sqlalchemy import select


class MemberCrud(CrudRepository):
    async def get_all_by_filter_pagination(
        self, filters: dict, limit: int, offset: int, db: AsyncSession
    ):  # noqa
        query = select(self.model).filter_by(**filters).limit(limit).offset(offset)
        result = await db.execute(query)
        return result.scalars().all()


member_crud = MemberCrud(MemberModel)