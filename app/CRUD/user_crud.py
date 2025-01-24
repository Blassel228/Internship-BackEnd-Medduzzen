import logging
from typing import Sequence
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import UserModel
from app.repositories.crud_repository import CrudRepository
from app.utils.deps import pwd_context
from app.schemas.schemas import UserCreateSchema
from app.schemas.schemas import UserGetSchema
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class UserCrud(CrudRepository):
    async def get_one(self, id_: int, db: AsyncSession):
        res = await db.scalar(select(self.model).where(self.model.id == id_))
        if res is None:
            raise HTTPException(status_code=404, detail="User was not found")
        return res

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 10
    ) -> Sequence:
        query = select(self.model).offset(skip).limit(limit)
        res = await db.scalars(query)
        users = res.all()
        if not users:
            logger.info("No users found with the given parameters.")
            raise HTTPException(status_code=404, detail="No users found")
        logger.info(f"Retrieved {len(users)} users.")
        return users

    async def add(self, data: UserCreateSchema, db: AsyncSession) -> UserGetSchema:
        data = data.model_dump(exclude_none=True)
        hashed_password = pwd_context.hash(data.pop("password"))
        data["hashed_password"] = hashed_password
        stmt = insert(self.model).values(**data)

        await db.execute(stmt)
        await db.commit()

        return UserGetSchema(**data)

    async def update(self, id_: int, data: BaseModel, db: AsyncSession) -> dict:
        try:
            data = data.model_dump(exclude_none=True)
            if "password" in data:
                data["hashed_password"] = pwd_context.hash(data.pop("password"))
            stmt = update(self.model).values(**data).where(self.model.id == id_)
            await db.execute(stmt)
            await db.commit()
            return {"message": "User was updated"}
            # return UserGetSchema(username=data["username"])
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=500, detail="Something went wrong while updating the user"
            )


user_crud = UserCrud(UserModel)
