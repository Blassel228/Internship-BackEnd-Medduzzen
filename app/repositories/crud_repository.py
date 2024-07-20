import logging
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class CrudRepository:
    def __init__(self, model):
        self.model = model

    async def get_all(self, db: AsyncSession):
        res = await db.scalars(select(self.model))
        return res.all()

    async def get_one(self, id_: int, db: AsyncSession):
        res = await db.scalar(select(self.model).where(self.model.id == id_))
        return res

    async def add(self, data: BaseModel, db: AsyncSession):
        stmt = insert(self.model).values(**data.model_dump())
        try:
            await db.execute(stmt)
            await db.commit()
            res = await self.get_one(id_=data.id, db=db)
            return res
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            raise HTTPException(status_code=500, detail="Failed to add entity")

    async def update(self, id_: int, data: BaseModel, db: AsyncSession):

        stmt = (
            update(self.model).values(**data.model_dump()).where(self.model.id == id_)
        )
        try:
            res = await db.execute(stmt)
            if res.rowcount == 0:
                return None
            await db.commit()
            res = await self.get_one(id_=id_, db=db)
            return res
        except Exception as e:
            logger.error(f"Error updating entity: {e}")
            raise e

    async def delete(self, id_: int, db: AsyncSession):
        res = await self.get_one(id_=id_, db=db)
        if res is None:
            return None
        stmt = delete(self.model).where(self.model.id == id_)
        await db.execute(stmt)
        await db.commit()
        return res

    async def get_one_by_filter(self, db: AsyncSession, filters: dict):
        query = select(self.model).filter_by(**filters)
        result = await db.scalar(query)
        return result

    async def get_all_by_filter(self, db: AsyncSession, filters: dict):
        query = select(self.model).filter_by(**filters)
        result = await db.scalars(query)
        return result.all()
