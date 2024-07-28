from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import UserSelfUpdateSchema, UserUpdateInSchema
from app.utils.deps import pwd_context
from fastapi import HTTPException
from app.CRUD.user_crud import user_crud


class UserService:
    async def self_update(self, id_: int, db: AsyncSession, data: UserUpdateInSchema):
        if not isinstance(data, UserUpdateInSchema):
            raise HTTPException(
                status_code=422, detail="Request body is not valid JSON."
            )
        data = data.model_dump(exclude={"id", "email"}, exclude_none=True)
        if "password" in data:
            data["hashed_password"] = pwd_context.hash(data.pop("password"))
        if not data:
            raise HTTPException(detail="Data is not full-filled", status_code=403)
        res = await user_crud.update(id_=id_, data=UserSelfUpdateSchema(**data), db=db)
        return res


user_service = UserService()