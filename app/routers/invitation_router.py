from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.invitation_crud import invitation_crud
from app.schemas.schemas import InvitationCreateSchema
from app.services.invitation_service import invitation_service
from app.utils.deps import get_db, get_current_user

invitation_router = APIRouter(prefix="/invitation", tags=["Invitation"])


@invitation_router.get("/sent")
async def get_user_sent_invitations(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_crud.get_all_by_filter(
        filters={"recipient_id": current_user.id}, db=db
    )


@invitation_router.get("/company/{company_id}/sent")
async def get_owner_sent_invitations(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await invitation_service.owner_get_all_invitations(
        user_id=current_user.id, company_id=company_id, db=db
    )


@invitation_router.post("/")
async def send_invitation(
    data: InvitationCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await invitation_service.send_invitation(
        data=data, db=db, user_id=current_user.id
    )


@invitation_router.post("/{id_}/accept")
async def accept_invitation(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_service.accept_invitation(
        id_=id_, db=db, user_id=current_user.id
    )


@invitation_router.delete("/{id_}/reject")
async def reject_invitation(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_service.reject_invitation(
        id_=id_, db=db, user_id=current_user.id
    )


@invitation_router.delete("/{id_}")
async def delete_invitation_by_owner(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_service.delete_invitation_by_owner(
        db=db, id_=id_, user_id=current_user.id
    )
