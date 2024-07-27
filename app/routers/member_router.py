from app.utils.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.deps import get_current_user
from app.services.member_service import member_service
from app.CRUD.member_crud import member_crud
from fastapi import APIRouter, Depends

member_router = APIRouter(tags=["Member"], prefix="/member")


@member_router.get("/get_users_in_company")
async def get_users_in_company(
    company_id: int,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await member_service.get_users_in_company(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
        limit=limit,
        offset=offset,
    )


@member_router.get("/get_all")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await member_crud.get_all(db=db)


@member_router.get("/get_all_admins_in_company")
async def get_all_admins_in_company(
    company_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await member_service.get_all_admins_in_company(
        db=db, user_id=current_user.id, company_id=company_id
    )


@member_router.put("/promote_member_to_admin")
async def promote_member_to_admin(
    member_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await member_service.promote_member_to_admin(
        db=db, user_id=current_user.id, member_id=member_id, company_id=company_id
    )


@member_router.put("/demote_member_from_admin")
async def demote_member_from_admin(
    member_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await member_service.demote_member_from_admin(
        db=db, user_id=current_user.id, member_id=member_id, company_id=company_id
    )


@member_router.delete("/fire_user")
async def fire_user(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await member_service.fire_user(db=db, user_id=current_user.id, id_=id_)


@member_router.delete("/user_resign")
async def user_resign(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await member_service.user_resign(db=db, user_id=current_user.id)
