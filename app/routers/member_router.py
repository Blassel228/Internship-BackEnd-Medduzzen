from app.utils.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.deps import get_current_user
from app.services.member_service import member_service
from app.CRUD.member_crud import member_crud
from fastapi import APIRouter, Depends

member_router = APIRouter(tags=["member"], prefix="/member")


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
