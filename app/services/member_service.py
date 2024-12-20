from typing import Sequence
from app.db.models.member_model import MemberModel
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud


class MemberService:
    async def get_all_admins_in_company(
        self, user_id: int, company_id: int, db: AsyncSession
    ) -> Sequence:
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You do not own such a company")
        admins = await member_crud.get_all_by_filter(filters={"role": "admin"}, db=db)
        if not admins:
            raise HTTPException(status_code=404, detail="There are no admins")
        return admins

    async def promote_member_to_admin(
        self, user_id: int, member_id: int, company_id: int, db: AsyncSession
    ) -> MemberModel:
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You do not own the company")
        member = await member_crud.get_one(id_=member_id, db=db)
        if member is None or member not in company.members:
            raise HTTPException(
                status_code=404, detail="Member not found in this company"
            )
        member.role = "admin"
        await db.commit()
        await db.refresh(member)
        return member

    async def demote_member_from_admin(
        self, user_id: int, member_id: int, company_id: int, db: AsyncSession
    ) -> MemberModel:
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You do not own the company")
        member = await member_crud.get_one(id_=member_id, db=db)
        if member is None or member not in company.members:
            raise HTTPException(
                status_code=404, detail="Member not found in this company"
            )
        member.role = "member"
        await db.commit()
        await db.refresh(member)
        return member

    async def fire_user(self, id_: int, user_id: int, db: AsyncSession) -> MemberModel:
        member = await member_crud.get_one(id_=id_, db=db)
        if member is None:
            raise HTTPException(status_code=404, detail="There is no such a user")
        company = await company_crud.get_one(id_=member.company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Such a company was not found")
        if company.owner_id != user_id:
            raise HTTPException(
                status_code=403, detail="You are not the owner of the company"
            )
        await member_crud.delete(id_=id_, db=db)
        return member

    async def user_resign(self, db: AsyncSession, user_id: int) -> MemberModel:
        member = await member_crud.get_one(id_=user_id, db=db)
        if member is None:
            raise HTTPException(
                status_code=404, detail="You are not a member in any company"
            )
        await member_crud.delete(id_=user_id, db=db)
        return member

    async def get_users_in_company(
        self, db: AsyncSession, user_id: int, company_id: int, limit: int, offset: int
    ) -> Sequence:
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You do not own company")
        res = await member_crud.get_all_by_filter_pagination(
            filters={"company_id": company_id}, limit=limit, offset=offset, db=db
        )
        return res


member_service = MemberService()
