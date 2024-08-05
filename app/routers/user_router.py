from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.CRUD.user_crud import user_crud
from app.schemas.schemas import UserCreateSchema, UserUpdateInSchema
from app.services.user_service import user_service
from app.utils.deps import get_db, get_current_user

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.put("/self_update")
async def self_update(
    data: UserUpdateInSchema,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.self_update(id_=current_user.id, data=data, db=db)


@user_router.delete("/self_delete")
async def self_delete(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await user_crud.delete(id_=current_user.id, db=db)


@user_router.get("/")
async def list_users(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10
):
    """Retrieve a paginated list of users."""
    return await user_crud.get_all(db=db, skip=skip, limit=limit)


@user_router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific user by their ID."""
    return await user_crud.get_one(id_=user_id, db=db)


@user_router.post("/")
async def create_user(data: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    return await user_crud.add(data=data, db=db)


@user_router.put("/{user_id}")
async def update_user(
    user_id: int, data: UserUpdateInSchema, db: AsyncSession = Depends(get_db)
):
    """Update a specific user's details."""
    return await user_crud.update(id_=user_id, data=data, db=db)


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a specific user by their ID."""
    return await user_crud.delete(id_=user_id, db=db)
