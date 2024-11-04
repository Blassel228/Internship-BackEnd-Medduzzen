from fastapi import APIRouter, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.quiz_crud import quiz_crud
from app.schemas.schemas import QuizCreateSchema
from app.services.quiz_service import quiz_service
from app.utils.deps import get_db, get_current_user
from fastapi.responses import FileResponse

quiz_router = APIRouter(prefix="/quizzes", tags=["Quiz"])


@quiz_router.get("/")
async def get_quizzes_with_pagination(
    limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    return await quiz_crud.get_all_pagination(db=db, limit=limit, offset=offset)


@quiz_router.put("/{quiz_id}")
async def update_quiz(
    quiz_id: int,
    data: QuizCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_service.update(
        db=db, data=data, user_id=current_user.id, id_=quiz_id
    )


@quiz_router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await quiz_crud.delete(db=db, id_=quiz_id)


@quiz_router.post("/")
async def create_quiz(
    notification_text: str,
    company_id: int,
    quiz_data: QuizCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await quiz_service.create(
        db=db,
        quiz_data=quiz_data,
        user_id=current_user.id,
        company_id=company_id,
        notification_text=notification_text,
    )


@quiz_router.get("/{quiz_id}")
async def get_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    quiz = await quiz_crud.get_one(id_=quiz_id, db=db)
    return quiz


@quiz_router.post("/import_excel_quiz")
async def import_excel_quiz(
    file: UploadFile,
    company_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await quiz_service.parse_and_create_or_update_quiz_from_upload(
        file=file, db=db, company_id=company_id, user_id=user.id
    )
    encoded_result = jsonable_encoder(result)
    return encoded_result


@quiz_router.post("/{id_}/export")
async def export_single_quiz_to_excel(id_: int, db: AsyncSession = Depends(get_db)):
    file_path = await quiz_service.export_single_quiz_to_excel(id_=id_, db=db)
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="quiz_export.xlsx"
    )