import logging
from typing import Sequence, Optional
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CrudRepository:
    def __init__(self, model):
        self.model = model

    async def get_all(self, db: AsyncSession) -> Sequence:
        res = await db.scalars(select(self.model))
        return res.all()

    async def get_one(self, id_: int, db: AsyncSession) -> Optional:
        res = await db.scalar(select(self.model).where(self.model.id == id_))
        return res

    async def add(self, data: BaseModel, db: AsyncSession) -> Optional:
        stmt = insert(self.model).values(**data.model_dump())
        await db.execute(stmt)
        await db.commit()
        return await self.get_one(id_=data.id, db=db)

    async def update(self, id_: int, data: BaseModel, db: AsyncSession) -> Optional:
        stmt = (
            update(self.model).values(**data.model_dump()).where(self.model.id == id_)
        )
        result = await db.execute(stmt)
        if result.rowcount == 0:
            return None
        await db.commit()
        return await self.get_one(id_=id_, db=db)

    async def delete(self, id_: int, db: AsyncSession) -> Optional:
        res = await self.get_one(id_=id_, db=db)
        if res is None:
            return None
        stmt = delete(self.model).where(self.model.id == id_)
        await db.execute(stmt)
        await db.commit()
        return res

    async def get_one_by_filter(self, db: AsyncSession, filters: dict) -> Optional:
        query = select(self.model).filter_by(**filters)
        result = await db.scalar(query)
        return result

    async def get_all_by_filter(self, db: AsyncSession, filters: dict) -> Sequence:
        stmt = select(self.model).filter_by(**filters)
        result = await db.scalars(stmt)
        return result.all()

    async def delete_all_by_filters(self, db: AsyncSession, filters: dict) -> Sequence:
        res = await self.get_all_by_filter(filters=filters, db=db)
        stmt = delete(self.model).filter_by(**filters)
        await db.execute(stmt)
        await db.commit()
        return res
