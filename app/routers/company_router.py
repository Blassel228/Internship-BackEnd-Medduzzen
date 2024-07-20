from fastapi import APIRouter
from app.CRUD.company_crud import company_crud
from app.utils.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import (
    CompanyCreateSchema,
    CompanyCreateInSchema,
    CompanyUpdateSchema,
    CompanyUpdateVisibility,
)
from fastapi import Depends

company_router = APIRouter(prefix="/company", tags=["Company"])


@company_router.get("/get_all_visible")
async def get_all_visible(db: AsyncSession = Depends(get_db)):
    return await company_crud.get_all_visible(db=db)


@company_router.get("/get_one_visible")
async def get_one_visible(id_: int, db: AsyncSession = Depends(get_db)):
    return await company_crud.get_one_visible(id_=id_, db=db)


@company_router.post("/add")
async def add(
    data: CompanyCreateInSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await company_crud.add(
        data=CompanyCreateSchema(**data.model_dump(), owner_id=current_user.id), db=db
    )


@company_router.put("/update")
async def update(
    id_: int,
    data: CompanyUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await company_crud.update(id_=id_, user_id=current_user.id, data=data, db=db)


@company_router.put("/update_visibility")
async def update_visibility(
    id_: int,
    data: CompanyUpdateVisibility,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await company_crud.update(id_=id_, user_id=current_user.id, data=data, db=db)


@company_router.delete("/delete_by_owner")
async def delete_by_owner(
    id_: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await company_crud.delete_by_owner(id_=id_, user_id=current_user.id, db=db)
