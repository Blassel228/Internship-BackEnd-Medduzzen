import logging
from typing import Sequence
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import UserModel
from app.repositories.crud_repository import CrudRepository
from app.schemas.schemas import UserCreateSchema
from app.utils.deps import pwd_context

logger = logging.getLogger(__name__)


class UserCrud(CrudRepository):
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

    async def add(self, data: UserCreateSchema, db: AsyncSession) -> UserModel:
        data = data.model_dump()
        hashed_password = pwd_context.hash(data.pop("password"))
        data["hashed_password"] = hashed_password
        stmt = insert(self.model).values(**data)

        try:
            await db.execute(stmt)
            await db.commit()
            res = await self.get_one(id_=data["id"], db=db)
            if res is None:
                logger.error(
                    "Failed to add user: User retrieval after insertion failed."
                )
                raise HTTPException(
                    status_code=500, detail="Something went wrong when adding a user"
                )
            logger.info(f"User {data['username']} added successfully.")
            return res
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise HTTPException(
                status_code=500, detail="Something went wrong when adding a user"
            )

    async def update(self, id_: int, data: BaseModel, db: AsyncSession) -> UserModel:
        res = await self.get_one(id_=id_, db=db)
        if res is None:
            raise HTTPException(status_code=404, detail="User was not found")
        try:
            data = data.model_dump(exclude_none=True)
            if "password" in data:
                data["hashed_password"] = pwd_context.hash(data.pop("password"))
            stmt = update(self.model).values(**data).where(self.model.id == id_)
            await db.execute(stmt)
            if "id" in data:
                res = await self.get_one(id_=data["id"], db=db)
            else:
                res = await self.get_one(id_=id_, db=db)
            await db.commit()
            return res
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=500, detail="Something went wrong while updating the user"
            )


user_crud = UserCrud(UserModel)
