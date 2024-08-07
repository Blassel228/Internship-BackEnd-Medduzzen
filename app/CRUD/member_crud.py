from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.member_model import MemberModel
from app.repositories.crud_repository import CrudRepository


class MemberCrud(CrudRepository):
    async def get_all_by_filter_pagination(
        self, filters: dict, limit: int, offset: int, db: AsyncSession
    ) -> Sequence:  # noqa
        stmt = select(self.model).filter_by(**filters).limit(limit).offset(offset)
        result = await db.execute(stmt)
        return result.scalars().all()


member_crud = MemberCrud(MemberModel)
