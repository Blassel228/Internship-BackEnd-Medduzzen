from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.CRUD.company_crud import company_crud
from app.CRUD.quiz_result_crud import quiz_result_crud
from app.CRUD.option_crud import option_crud
from app.CRUD.user_crud import user_crud
from app.CRUD.quiz_crud import quiz_crud
from app.CRUD.member_crud import member_crud
from app.db.models.models import QuizResultModel
from app.schemas.schemas import (
    QuizResultCreateInSchema,
    QuizResultCreateSchema,
    QuizResultUpdateSchema,
)
from app.services.redis_service import redis_service


class QuizResultService:
    async def user_get_its_result(self, user_id: int, db: AsyncSession):
        results = await quiz_result_crud.get_all_by_filter(
            db=db, filters={"user_id": user_id}
        )
        return results

    async def get_all_company_results(
        self, user_id: int, company_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await member_crud.get_one(id_=company_id, db=db)
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have such rights")
        company = await company_crud.get_one(id_=member.company_id, db=db)
        if member.company_id != company.id:
            raise HTTPException(
                status_code=403, detail="You are not a member of the company"
            )

        results = await quiz_result_crud.get_all_by_filter(
            db=db, filters={"company_id": company_id}
        )
        return results

    async def get_results_for_user(
        self, user_id: int, id_: int, company_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await member_crud.get_one(id_=company_id, db=db)
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have such rights")
        company = await company_crud.get_one(id_=member.company_id, db=db)
        if member.company_id != company.id:
            raise HTTPException(
                status_code=403, detail="You are not a member of the company"
            )

        results = await quiz_result_crud.get_all_by_filter(
            db=db, filters={"user_id": id_}
        )
        return results

    async def pass_quiz(
        self, data: QuizResultCreateInSchema, user_id: int, db: AsyncSession
    ):
        user = await user_crud.get_one(id_=user_id, db=db)
        quiz_result = await quiz_result_crud.get_one(id_=data.id, db=db)
        if quiz_result is not None:
            if quiz_result.user_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Result with such an id already exist for another user",
                )
        quiz = await quiz_crud.get_one(id_=data.quiz_id, db=db)
        if quiz is None:
            raise HTTPException(status_code=404, detail="There is not such a quiz")
        company = await company_crud.get_one(id_=quiz.company_id, db=db)
        member = await member_crud.get_one(id_=user_id, db=db)
        if member is None:
            if user_id != company.owner_id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
        if len(quiz.questions) != len(data.options_ids):
            raise HTTPException(
                status_code=403, detail="Invalid number of options provided"
            )
        right_answers = 0
        user_answers = {}
        questions_info = {}
        for question, provided_option in zip(quiz.questions, data.options_ids):
            option = await option_crud.get_one(id_=provided_option, db=db)
            if option.question_id != question.id:
                raise HTTPException(
                    status_code=403,
                    detail="Option provided do not comply with the question",
                )

            if option.is_correct is True:
                right_answers += 1

            user_answers[question.id] = {
                f"provided_option_{question.id}": provided_option,
                f"is_correct_{question.id}": option.is_correct,
            }

            questions_info[question.id] = {
                f"question_text_{question.id}": question.text
            }

        score = round(right_answers / len(quiz.questions), 2)
        previous_result = await quiz_result_crud.get_one_by_filter(
            filters={"quiz_id": quiz.id, "user_id": user_id}, db=db
        )
        if previous_result is not None:
            res = await quiz_result_crud.update(
                id_=previous_result.id,
                data=QuizResultUpdateSchema(
                    score=score, registration_date=str(datetime.now())
                ),
                db=db,
            )
        else:
            res = await quiz_result_crud.add(
                data=QuizResultCreateSchema(
                    id=data.id,
                    quiz_id=quiz.id,
                    company_id=company.id,
                    score=score,
                    user_id=user_id,
                ),
                db=db,
            )
        user_answers = {
            key: value
            for answer in user_answers.values()
            for key, value in answer.items()
        }
        questions_info = {
            key: value
            for answer in questions_info.values()
            for key, value in answer.items()
        }
        result_data = {
            "quiz_id": quiz.id,
            "quiz_name": quiz.name,
            "quiz_description": quiz.description,
            "company_id": company.id,
            "company_name": company.name,
            "company_description": company.description,
            "user_id": user.id,
            "user_email": user.email,
            **questions_info,
            "score": score,
            **user_answers,
        }
        await redis_service.cache_quiz_result(data=result_data)

        return res

    async def get_average_score_for_company(self, db: AsyncSession, company_id: int):
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="Such a company does not exist")
        stmt = (
            select(
                QuizResultModel.user_id,
                func.avg(QuizResultModel.score).label("average_score"),
            ).where(QuizResultModel.company_id == company_id)
        ).group_by(QuizResultModel.user_id)
        result = await db.execute(stmt)
        return result.iterator

    async def get_average_score_for_all(self, db: AsyncSession):
        stmt = select(
            QuizResultModel.user_id,
            func.avg(QuizResultModel.score).label("average_score"),
        ).group_by(QuizResultModel.user_id)
        result = await db.execute(stmt)
        return result.iterator


quiz_result_service = QuizResultService()
