from fastapi import APIRouter
from app.services.quiz_service import quiz_service
from app.utils.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import QuizCreateSchema
from fastapi import Depends


quiz_router = APIRouter(prefix="/quiz", tags=["Quiz"])


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
    company_id: int,
    data: QuizCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_service.update(
        db=db, data=data, user_id=current_user.id, company_id=company_id, id_=id_
    )
