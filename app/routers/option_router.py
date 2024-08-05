from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.CRUD.option_crud import option_crud
from app.utils.deps import get_db

option_router = APIRouter(tags=["Option"], prefix="/option")


@option_router.get("/get_all")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await option_crud.get_all(db=db)


@option_router.delete("/")
async def delete(id_: int, db: AsyncSession = Depends(get_db)):
    return await option_crud.delete(id_=id_, db=db)
