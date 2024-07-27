from app.utils.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.CRUD.option_crud import option_crud

option_router = APIRouter(tags=["Option"], prefix="/option")


@option_router.get("/get_all")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await option_crud.get_all(db=db)
