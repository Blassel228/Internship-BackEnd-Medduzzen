import base64
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.crud_repository import CrudRepository
from app.db.models.image_model import ImageModel
from app.schemas.schemas import CreateImage, ImageResponse, ImageResponseByte
from fastapi import UploadFile, Depends, HTTPException

from app.utils.deps import get_db


class ImageCrud(CrudRepository):
    async def get_all(self, db:AsyncSession):
        res = await db.scalars(select(self.model))
        response_list = []
        for image in res:
            image = ImageResponse(file_name=image.file_name)
            response_list.append(image)
        return response_list


    async def get_one(self, id_: int, db: AsyncSession = Depends(get_db)):
        stmt = select(ImageModel).filter(ImageModel.id == id_)
        image = await db.scalar(stmt)

        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")

        encoded_image = base64.b64encode(image.image_data).decode('utf-8')

        return ImageResponse(
            file_name=image.file_name,
            image_data=encoded_image
        )


    async def add(self, file: UploadFile, db: AsyncSession, user_id: int):
        image_data = await file.read()
        data = CreateImage(
            user_id=user_id, file_name=file.filename, image_data=image_data
        )
        stmt = insert(ImageModel).values(**data.model_dump())
        encoded_image = base64.b64encode(data.image_data).decode('utf-8')
        await db.execute(stmt)
        await db.commit()
        return ImageResponse(file_name=file.filename, image_data=encoded_image)


    async def get_one_by_filter(self, db: AsyncSession, filters: dict) -> Optional:
        query = select(self.model).filter_by(**filters)
        image = await db.scalar(query)
        encoded_image = base64.b64encode(image.image_data).decode('utf-8')
        return ImageResponse(
            id=image.id,
            file_name=image.file_name,
            image_data=encoded_image
        )


    async def delete_one_by_filter(self, db: AsyncSession, filters: dict) -> Optional:
        image = await self.get_one_by_filter(filters=filters, db=db)
        stmt = delete(self.model).filter_by(**filters)
        await db.execute(stmt)
        await db.commit()
        return image


image_crud = ImageCrud(ImageModel)
