from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.image_service import image_service
from app.utils.deps import get_db
from app.CRUD.image_crud import image_crud
from app.utils.deps import get_current_user

image_router = APIRouter(prefix="/image", tags=["Image"])


@image_router.post("/")
async def add(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await image_crud.add(file=file, user_id=user.id, db=db)


@image_router.get("/{id_}")
async def get_one(id_: int, db: AsyncSession = Depends(get_db)):
    return await image_crud.get_one(db=db, id_=id_)


@image_router.get("/")
async def get_all(db=Depends(get_db)):
    return await image_crud.get_all(db=db)


@image_router.get("/get_one_by_user_id/{user_id}")
async def get_one_by_filter(user_id: int, db=Depends(get_db)):
    return await image_crud.get_one_by_filter(db=db, filters={"user_id": user_id})


@image_router.post("/upload_new_image")
async def upload_new_image(file: UploadFile, user=Depends(get_current_user), db=Depends(get_db)):
    return await image_service.upload_new_image(file=file, user_id=user.id, db=db)
