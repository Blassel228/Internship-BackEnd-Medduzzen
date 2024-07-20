from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud
from fastapi import HTTPException


class MemberService:
    async def fire_user(self, id_: int, user_id: int, db: AsyncSession):
        member = await member_crud.get_one(id_=id_, db=db)
        if member is None:
            raise HTTPException(status_code=404, detail="There is no such a user")
        company = await company_crud.get_one(id_=member.company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Such a company was not found")
        if company.owner_id != user_id:
            raise HTTPException(
                status_code=403, detail="You are no the owner of the company"
            )
        await member_crud.delete(id_=id_, db=db)
        return member

    async def user_resign(self, db: AsyncSession, user_id: int):
        member = await member_crud.get_one(id_=user_id, db=db)
        if member is None:
            raise HTTPException(
                status_code=403, detail="You are not a member in any company"
            )
        await member_crud.delete(id_=user_id, db=db)
        return member

    async def get_users_in_company(
        self, db: AsyncSession, user_id: int, company_id: int, limit: int, offset: int
    ):
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You do not own company")
        res = await member_crud.get_all_by_filter(
            filters={"company_id": company_id}, limit=limit, offset=offset, db=db
        )
        return res


member_service = MemberService()
