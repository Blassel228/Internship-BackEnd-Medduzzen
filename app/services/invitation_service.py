from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.company_crud import company_crud
from app.CRUD.invitation_crud import invitation_crud
from fastapi import HTTPException
from app.schemas.schemas import InvitationCreateSchema, MemberCreateSchema
from app.CRUD.member_crud import member_crud


class InvitationService:
    async def owner_get_all_invitations(
        self, user_id: int, company_id: int, db: AsyncSession
    ):
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Such a company does not exist")
        if user_id != company.owner_id:
            raise HTTPException(
                status_code=403,
                detail="You do not own the company to get the invitations",
            )
        invitations = await invitation_crud.get_all_by_filter(
            filters={"company_id": company_id}, db=db
        )
        return invitations

    async def send_invitation(
        self, user_id: int, data: InvitationCreateSchema, db: AsyncSession
    ):
        invitation = await invitation_crud.get_one(id_=data.id, db=db)
        if invitation is not None:
            raise HTTPException(
                status_code=409, detail="Such an invitation already exists"
            )
        if data.recipient_id == user_id:
            raise HTTPException(
                status_code=403, detail="Cannot send invitation to itself"
            )
        company = await company_crud.get_one(id_=data.company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if company.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not own the company to send invitations",
            )
        member = await member_crud.get_one(id_=data.recipient_id, db=db)
        if member is not None:
            if member.company_id == data.company_id:
                raise HTTPException(
                    status_code=400, detail="The user is in your company already"
                )
        invitation = await invitation_crud.add(data=data, db=db)
        return invitation

    async def delete_invitation_by_owner(
        self, id_: int, user_id: int, db: AsyncSession
    ):
        invitation = await invitation_crud.get_one(id_=id_, db=db)
        if invitation is None:
            raise HTTPException(
                status_code=404, detail="Such an invitation does not exist"
            )
        company = await company_crud.get_one(id_=invitation.company_id, db=db)
        if company.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not possess the compony to delete invitations",
            )
        await invitation_crud.delete(id_=id_, db=db)
        return invitation

    async def accept_invitation(self, id_: int, user_id: int, db: AsyncSession):
        member = await member_crud.get_one(db=db, id_=user_id)
        if member is not None:
            raise HTTPException(status_code=403, detail="You are in a company already")
        invitation = await invitation_crud.get_one(id_=id_, db=db)
        if invitation is None:
            raise HTTPException(
                status_code=404, detail="The invitation with such an id does not exist"
            )
        if invitation.recipient_id != user_id:
            raise HTTPException(
                status_code=409, detail="You do not have such an invitation to accept"
            )
        company = await company_crud.get_one(id_=invitation.company_id, db=db)
        member = await member_crud.add(
            db=db, data=MemberCreateSchema(company_id=company.id, id=user_id)
        )
        await invitation_crud.delete(id_=id_, db=db)
        return member

    async def reject_invitation(self, id_: int, user_id: int, db: AsyncSession):
        invitation = await invitation_crud.get_one(id_=id_, db=db)
        if invitation is None:
            raise HTTPException(
                status_code=404, detail="The invitation with such an id does not exist"
            )
        if invitation.recipient_id != user_id:
            raise HTTPException(
                status_code=404, detail="You do not have such a invitation to delete"
            )
        await invitation_crud.delete(id_=invitation.id, db=db)
        return invitation


invitation_service = InvitationService()
