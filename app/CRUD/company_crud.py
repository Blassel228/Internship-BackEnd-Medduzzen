from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from sqlalchemy.sql.operators import and_
from app.db.models.models import CompanyModel
from app.repositories.crud_repository import CrudRepository
from fastapi import HTTPException
from app.schemas.schemas import CompanyUpdateSchema


class CompanyCrud(CrudRepository):
    async def get_all_visible(self, db: AsyncSession):
        stmt = select(self.model).where(self.model.visible == True)
        res = await db.scalars(stmt)
        return res.all()

    async def get_one_visible(self, id_: int, db: AsyncSession):
        stmt = select(self.model).where(
            and_(self.model.id == id_, self.model.visible == True)
        )
        res = await db.scalar(stmt)
        return res

    async def delete_by_owner(self, id_: int, user_id: int, db: AsyncSession):  # noqa
        res = await self.get_one(db=db, id_=id_)
        if res is None:
            raise HTTPException(
                status_code=404,
                detail="Company you are trying to delete does not exist",
            )
        if res.owner_id == user_id:
            res = await self.delete(db=db, id_=id_)
        else:
            raise HTTPException(
                status_code=403,
                detail="You do not possess company you are trying to delete",
            )
        return res

    async def update(
        self, id_: int, user_id: int, db: AsyncSession, data: CompanyUpdateSchema
    ):  # noqa
        res = await self.get_one(db=db, id_=id_)
        if res is None:
            raise HTTPException(
                status_code=404,
                detail="Company you are trying to change does not exist",
            )
        if user_id == res.owner_id:
            stmt = (
                update(self.model).values(data.model_dump()).where(self.model.id == id_)
            )
            await db.execute(stmt)
            await db.commit()
        else:
            raise HTTPException(
                status_code=403,
                detail="You do not possess company you are trying to update",
            )
        res = await self.get_one(db=db, id_=id_)
        return res


company_crud = CompanyCrud(CompanyModel)
