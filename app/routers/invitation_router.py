from fastapi import APIRouter
from app.schemas.schemas import InvitationCreateSchema
from app.CRUD.invitation_crud import invitation_crud
from app.services.invitation_service import invitation_service
from app.utils.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


invitation_router = APIRouter(prefix="/invitation", tags=["Invitation"])


@invitation_router.get("/user_get_all_sent_invitations")
async def user_get_all_sent_invitations(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_crud.get_all_by_filter(
        filters={"recipient_id": current_user.id}, db=db
    )


@invitation_router.get("/owner_get_all_sent_invitations")
async def owner_get_all_sent_invitations(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await invitation_service.owner_get_all_invitations(
        user_id=current_user.id, company_id=company_id, db=db
    )


@invitation_router.post("/send_invitation")
async def send_invitation(
    data: InvitationCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await invitation_service.send_invitation(
        data=data, db=db, user_id=current_user.id
    )


@invitation_router.post("/accept_invitation")
async def accept_invitation(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_service.accept_invitation(
        id_=id_, db=db, user_id=current_user.id
    )


@invitation_router.delete("/reject_invitation")
async def reject_invitation(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_service.reject_invitation(
        id_=id_, db=db, user_id=current_user.id
    )


@invitation_router.delete("/delete_invitation_by_owner")
async def delete_invitation_by_owner(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await invitation_service.delete_invitation_by_owner(
        db=db, id_=id_, user_id=current_user.id
    )
