from fastapi import APIRouter
from app.CRUD.user_crud import user_crud
from app.utils.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserCreateSchema, UserUpdateInSchema
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
    id_: int, data: UserUpdateInSchema, db: AsyncSession = Depends(get_db)
):
    return await user_crud.user_update(id_=id_, data=data, db=db)


@user_router.delete("/")
async def delete(id_: int, db: AsyncSession = Depends(get_db)):
    return await user_crud.delete(id_=id_, db=db)
