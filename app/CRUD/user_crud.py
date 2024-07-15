import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserCreateSchema, UserUpdateSchema, UserUpdateInSchema
from sqlalchemy.dialects.postgresql import insert
from app.utils.deps import pwd_context
from app.repositories.crud_repository import CrudRepository
from app.db.models import UserModel
from fastapi import HTTPException
from sqlalchemy import select

logger = logging.getLogger(__name__)

class UserCrud(CrudRepository):
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 10):
        query = select(self.model).offset(skip).limit(limit)
        res = await db.scalars(query)
        users = res.all()
        if not users:
            logger.info("No users found with the given parameters.")
            raise HTTPException(status_code=404, detail="No users found")
        logger.info(f"Retrieved {len(users)} users.")
        return users

    async def add(self, data: UserCreateSchema, db: AsyncSession):
        data = data.model_dump()
        hashed_password = pwd_context.hash(data.pop("password"))
        data['hashed_password'] = hashed_password
        stmt = insert(self.model).values(**data)

        try:
            await db.execute(stmt)
            await db.commit()
            res = await self.get_one(id_=data["id"], db=db)
            if res is None:
                logger.error("Failed to add user: User retrieval after insertion failed.")
                raise HTTPException(status_code=500, detail="Something went wrong when adding a user")
            logger.info(f"User {data['username']} added successfully.")
            return res
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise HTTPException(status_code=500, detail="Something went wrong when adding a user")

    async def user_update(self, id_: int, data: UserUpdateInSchema, db: AsyncSession):
        data = data.model_dump()
        hashed_password = pwd_context.hash(data.pop("password"))
        data['hashed_password'] = hashed_password
        try:
            res = await self.update(id_=id_, data=UserUpdateSchema(**data), db=db)
            if res is None:
                raise HTTPException(status_code=404, detail="User is not valid")
            return res
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(status_code=500, detail="Something went wrong while updating the user")

user_crud = UserCrud(UserModel)