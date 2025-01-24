from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.user_crud import user_crud
from app.schemas.schemas import (
    UserSelfUpdateSchema,
    UserUpdateInSchema,
    UserCreateSchema,
)
from app.utils.deps import pwd_context
from fastapi import HTTPException


class UserService:
    async def self_update(
        self, id_: int, db: AsyncSession, data: UserUpdateInSchema
    ) -> dict:
        data = data.model_dump(exclude={"id", "email"}, exclude_none=True)
        if "password" in data:
            data["hashed_password"] = pwd_context.hash(data.pop("password"))
        res = await user_crud.update(id_=id_, data=UserSelfUpdateSchema(**data), db=db)
        return res

    async def register_user(self, db: AsyncSession, user_data: UserCreateSchema):
        existing_user = await self.check_user_exists(
            db, email=user_data.email, username=user_data.username
        )

        if existing_user["exists"]:
            raise HTTPException(
                status_code=400,
                detail=f"User with this {existing_user['field']} already exists.",
            )

        return await user_crud.add(db=db, data=user_data)

    async def check_user_exists(
        self, db: AsyncSession, email: str = None, username: str = None
    ):
        if email:
            user_by_email = await user_crud.get_one_by_filter(
                filters={"email": email}, db=db
            )
            if user_by_email:
                return {
                    "exists": True,
                    "field": "email",
                    "message": "User with this email already exists.",
                }

        if username:
            user_by_username = await user_crud.get_one_by_filter(
                filters={"username": username}, db=db
            )
            if user_by_username:
                return {
                    "exists": True,
                    "field": "username",
                    "message": "User with this username already exists.",
                }

        return {
            "exists": False,
            "message": "No user found with the provided email or username.",
        }


user_service = UserService()
