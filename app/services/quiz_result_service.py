from dataclasses import asdict
from datetime import datetime, timedelta
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.sql.operators import and_


from app.CRUD.company_crud import company_crud
from app.CRUD.quiz_result_crud import quiz_result_crud
from app.CRUD.option_crud import option_crud
from app.CRUD.user_crud import user_crud
from app.CRUD.quiz_crud import quiz_crud
from app.CRUD.member_crud import member_crud
from app.db.models.models import QuizResultModel, QuizModel, UserModel
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
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
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
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
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
            raise HTTPException(
                status_code=403, detail="Result with such an id already exists"
            )
        quiz = await quiz_crud.get_one(id_=data.quiz_id, db=db)
        if quiz is None:
            raise HTTPException(status_code=404, detail="There is no such a quiz")
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
            if option is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"There is no such an option with id {provided_option}",
                )
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

    async def get_user_average_score(self, user_id: int, db: AsyncSession):
        result = await db.execute(
            select(func.avg(QuizResultModel.score)).where(
                QuizResultModel.user_id == user_id
            )
        )
        if result is None:
            raise HTTPException(status_code=404, detail="You have no results")
        avg_score = result.scalar()
        return avg_score

    async def get_average_score_for_all(self, db: AsyncSession, company_id: int):
        stmt = select(
            QuizResultModel.user_id,
            func.avg(QuizResultModel.score).label("average_score"),
        ).where(QuizResultModel.company_id == company_id)
        result = await db.execute(stmt)
        return result.iterator

    async def get_user_quiz_averages_with_time_ranges(
            self, user_id: int, id_: int, company_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
            if member.company_id != company.id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of the company"
                )
        stmt = (
            select(
                QuizResultModel.user_id,
                QuizResultModel.quiz_id,
                QuizModel.name.label("quiz_name"),
                func.avg(QuizResultModel.score).label("average_score"),
                func.min(QuizResultModel.registration_date).label("start_time"),
                func.max(QuizResultModel.registration_date).label("end_time"),
            )
            .join(QuizModel, QuizResultModel.quiz_id == QuizModel.id)
            .where(
                and_(
                    QuizResultModel.user_id == id_,
                    QuizResultModel.company_id == company_id,
                )
            )
            .group_by(
                QuizResultModel.user_id,
                QuizResultModel.quiz_id,
                QuizModel.name
            )
        )
        result = await db.execute(stmt)
        quiz_averages_with_time_ranges = result.fetchall()

        if not quiz_averages_with_time_ranges:
            raise HTTPException(
                status_code=404, detail="No quiz results found for the user."
            )

        result_list = [row._asdict() for row in quiz_averages_with_time_ranges]

        return result_list

    async def get_quizzes_with_last_completion(
        self, company_id: int, user_id: int, id_: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
            if member.company_id != company.id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of the company"
                )
        stmt = (
            select(
                QuizResultModel.user_id,
                QuizResultModel.quiz_id,
                QuizModel.name.label("quiz_name"),
                func.max(QuizResultModel.registration_date).label("last_completion"),
            )
            .join(QuizModel, QuizResultModel.quiz_id == QuizModel.id)
            .where(
                and_(
                    QuizResultModel.user_id == id_,
                    QuizResultModel.company_id == company_id,
                )
            )
            .group_by(QuizResultModel.user_id, QuizResultModel.quiz_id, QuizModel.name)
        )

        result = await db.execute(stmt)
        quizzes_with_last_completion = result.all()

        if not quizzes_with_last_completion:
            raise HTTPException(
                status_code=404, detail="No quiz results found for the user."
            )

        result_list = [row._asdict() for row in quizzes_with_last_completion]
        return result_list

    async def get_company_results_last_week(
        self, user_id: int, company_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
            if member.company_id != company.id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of the company"
                )

        one_week_ago = datetime.now() - timedelta(days=7)

        stmt = (
            select(
                QuizResultModel.user_id,
                QuizResultModel.quiz_id,
                QuizResultModel.score,
                QuizResultModel.registration_date,
            )
            .where(
                and_(
                    QuizResultModel.company_id == company_id,
                    QuizResultModel.registration_date >= one_week_ago,
                )
            )
            .order_by(QuizResultModel.registration_date)
        )

        result = await db.execute(stmt)
        results_last_week = result.fetchall()

        if not results_last_week:
            raise HTTPException(
                status_code=404, detail="No quiz results found for the last week."
            )

        result_list = [row._asdict() for row in results_last_week]
        return result_list

    async def get_user_quiz_averages_last_week(
        self, user_id: int, id_: int, company_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
            if member.company_id != company.id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of the company"
                )

        one_week_ago = datetime.now() - timedelta(days=7)

        stmt = (
            select(
                QuizResultModel.user_id,
                QuizResultModel.quiz_id,
                QuizModel.name.label("quiz_name"),
                func.avg(QuizResultModel.score).label("average_score"),
            )
            .join(QuizModel, QuizResultModel.quiz_id == QuizModel.id)
            .where(
                QuizResultModel.user_id == id_,
                QuizResultModel.company_id == company_id,
                QuizResultModel.registration_date >= one_week_ago,
            )
            .group_by(QuizResultModel.user_id, QuizResultModel.quiz_id, QuizModel.name)
            .order_by(QuizResultModel.quiz_id)
        )

        result = await db.execute(stmt)
        quiz_averages_last_week = result.all()

        if not quiz_averages_last_week:
            raise HTTPException(
                status_code=404,
                detail="No quiz results found for the user in the last week.",
            )

        result_list = [row._asdict() for row in quiz_averages_last_week]
        return result_list

    async def get_all_company_users_last_attempt(
        self, user_id: int, company_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one(id_=company_id, db=db)
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
            if member.company_id != company.id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of the company"
                )

        stmt = (
            select(
                UserModel.id.label("user_id"),
                UserModel.username.label("username"),
                func.max(QuizResultModel.registration_date).label("last_attempt"),
            )
            .join(QuizResultModel, QuizResultModel.user_id == UserModel.id)
            .where(QuizResultModel.company_id == company_id)
            .group_by(UserModel.id, UserModel.username)
            .order_by(UserModel.id)
        )

        result = await db.execute(stmt)
        users_last_attempt = result.all()

        if not users_last_attempt:
            raise HTTPException(
                status_code=404, detail="No quiz attempts found for the company."
            )

        result_list = [row._asdict() for row in users_last_attempt]
        return result_list


quiz_result_service = QuizResultService()
