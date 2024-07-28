from fastapi import APIRouter
from app.CRUD.quiz_result_crud import quiz_result_crud
from app.schemas.schemas import QuizResultCreateInSchema
from app.services.quiz_result_service import quiz_result_service
from app.utils.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


quiz_result_router = APIRouter(prefix="/quiz_result_router", tags=["Quiz_Result"])


@quiz_result_router.get("/get_all")
async def get_all(db: AsyncSession = Depends(get_db)):
    return await quiz_result_crud.get_all(db=db)


@quiz_result_router.delete("/delete")
async def delete(id_: int, db: AsyncSession = Depends(get_db)):
    return await quiz_result_crud.delete(id_=id_, db=db)


@quiz_result_router.get("/get_results_for_user")
async def get_results_for_user(
    id_: int,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.get_results_for_user(
        id_=id_, company_id=company_id, user_id=current_user.id, db=db
    )


@quiz_result_router.get("/get_all_company_results")
async def get_all_company_results(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
        return await quiz_result_service.get_all_company_results(
        company_id=company_id, user_id=current_user.id, db=db
    )


@quiz_result_router.post("/pass_quiz")
async def pass_quiz(
    data: QuizResultCreateInSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.pass_quiz(
        db=db, data=data, user_id=current_user.id
    )


@quiz_result_router.get("/get_average_score_for_company")
async def get_average_score_for_company(
    company_id: int, db: AsyncSession = Depends(get_db)
):
    quiz = await quiz_result_service.get_average_score_for_company(
        company_id=company_id, db=db
    )
    return quiz


@quiz_result_router.get("/get_average_score_for_all")
async def get_average_score_for_all(db: AsyncSession = Depends(get_db)):
    quiz = await quiz_result_service.get_average_score_for_all(db=db)
    return quiz


@quiz_result_router.get("/get_user_quiz_averages_with_time_ranges")
async def get_user_quiz_averages_with_time_ranges(
    id_: int,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.get_user_quiz_averages_with_time_ranges(
        user_id=current_user.id, id_=id_, company_id=company_id, db=db
    )


@quiz_result_router.get("/get_quizzes_with_last_completion")
async def get_quizzes_with_last_completion(
    company_id: int,
    id_: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.get_quizzes_with_last_completion(
        company_id=company_id, user_id=current_user.id, id_=id_, db=db
    )


@quiz_result_router.get("/get_company_results_last_week")
async def get_company_results_last_week(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.get_company_results_last_week(
        user_id=current_user.id, company_id=company_id, db=db
    )


@quiz_result_router.get("/get_user_quiz_averages_last_week")
async def get_user_quiz_averages_last_week(
    id_: int,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.get_user_quiz_averages_last_week(
        user_id=current_user.id, id_=id_, company_id=company_id, db=db
    )


@quiz_result_router.get("/get_all_company_users_last_attempt")
async def get_all_company_users_last_attempt(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_result_service.get_all_company_users_last_attempt(
        user_id=current_user.id, company_id=company_id, db=db
    )


@quiz_result_router.get("/users/{user_id}/average-score")
async def read_user_average_score(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await quiz_result_service.get_user_average_score(user_id=current_user.id, db=db)
