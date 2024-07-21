from fastapi import APIRouter

from app.CRUD.quiz_crud import quiz_crud
from app.services.quiz_service import quiz_service
from app.utils.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import QuizCreateSchema
from fastapi import Depends


quiz_router = APIRouter(prefix="/quiz", tags=["Quiz"])


@quiz_router.get("/get_all_pagination")
async def get_all_pagination(
    limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    return await quiz_crud.get_all_pagination(db=db, limit=limit, offset=offset)


@quiz_router.post("/create")
async def create(
    company_id: int,
    quiz_data: QuizCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_service.create(
        db=db, quiz_data=quiz_data, user_id=current_user.id, company_id=company_id
    )


@quiz_router.put("/update")
async def update(
    id_: int,
    data: QuizCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_service.update(db=db, data=data, user_id=current_user.id, id_=id_)


@quiz_router.get("/get_one")
async def get_one(id_: int, db: AsyncSession = Depends(get_db)):
    quiz = await quiz_crud.get_one(id_=id_, db=db)
    return quiz
