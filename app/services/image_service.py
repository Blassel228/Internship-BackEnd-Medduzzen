from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from app.CRUD.image_crud import image_crud

class ImageService:
    async def upload_new_image(self, file: UploadFile, db: AsyncSession, user_id: int):
        image = await image_crud.get_one_by_filter(db=db, filters={"user_id": user_id})
        if image:
            await image_crud.delete_one_by_filter(db=db, filters={"user_id": user_id})
        new_image = await image_crud.add(file=file, user_id=user_id, db=db)
        return new_image

image_service = ImageService()