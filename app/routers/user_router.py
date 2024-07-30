from fastapi import APIRouter
from app.CRUD.user_crud import user_crud
from app.services.user_service import user_service
from app.utils.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserCreateSchema, UserUpdateSchema, UserUpdateInSchema
from fastapi import Depends

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/")
async def get_all(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10):
    return await user_crud.get_all(db=db, skip=skip, limit=limit)


@user_router.get("/{user_id}")
async def get_one(id_: int, db: AsyncSession = Depends(get_db)):
    return await user_crud.get_one(id_=id_, db=db)


@user_router.post("/")
async def add(data: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    return await user_crud.add(data=data, db=db)


@user_router.put("/")
async def update(
    id_: int, data: UserUpdateSchema, db: AsyncSession = Depends(get_db)
):
    return await user_crud.user_update(id_=id_, data=data, db=db)


@user_router.delete("/self_delete")
async def self_delete(id_: int, db: AsyncSession = Depends(get_db)):
    return await user_crud.delete(id_=id_, db=db)


@user_router.put("/self_update")
async def self_update(
    data: UserUpdateInSchema,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.self_update(id_=current_user.id, data=data, db=db)


@user_router.delete("/self_delete")
async def self_delete(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await user_crud.delete(id_=current_user.id, db=db)
