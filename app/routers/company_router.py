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


@company_router.get("/visible")
async def get_all_visible_companies(db: AsyncSession = Depends(get_db)):
    return await company_crud.get_all_visible(db=db)


@company_router.get("/visible/{id_}")
async def get_visible_company(id_: int, db: AsyncSession = Depends(get_db)):
    return await company_crud.get_one_visible(id_=id_, db=db)


@company_router.post("/")
async def create_company(
    data: CompanyCreateInSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await company_crud.add(
        data=CompanyCreateSchema(**data.model_dump(), owner_id=current_user.id), db=db
    )


@company_router.put("/{id_}")
async def update_company(
    id_: int,
    data: CompanyUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await company_crud.update(id_=id_, user_id=current_user.id, data=data, db=db)


@company_router.put("/{id_}/visibility")
async def update_company_visibility(
    id_: int,
    data: CompanyUpdateVisibility,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await company_crud.update(id_=id_, user_id=current_user.id, data=data, db=db)


@company_router.delete("/{id_}/owner")
async def delete_company_by_owner(
    id_: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await company_crud.delete_by_owner(id_=id_, user_id=current_user.id, db=db)
