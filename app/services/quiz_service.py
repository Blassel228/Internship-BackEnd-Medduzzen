from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud
from app.CRUD.quiz_crud import quiz_crud
from app.CRUD.option_crud import option_crud
from app.CRUD.question_crud import question_crud
from app.schemas.schemas import QuizCreateSchema
from app.db.models.models import QuizModel, QuestionModel, OptionModel
from fastapi import HTTPException
from app.services.notification_service import notification_service


class QuizService:
    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        company_id: int,
        notification_text: str,
        quiz_data: QuizCreateSchema,
    ):
        try:
            company = await company_crud.get_one(id_=company_id, db=db)
            member = await member_crud.get_one(id_=user_id, db=db)
            if member is None or member.role != "admin":
                if user_id != company.owner_id:
                    raise HTTPException(
                        status_code=403, detail="You are not a member of this company."
                    )

            if len(quiz_data.questions) < 2:
                raise HTTPException(
                    status_code=400, detail="A quiz must have at least two questions."
                )
            new_quiz = QuizModel(
                id=quiz_data.id,
                company_id=company_id,
                name=quiz_data.name,
                description=quiz_data.description,
            )
            db.add(new_quiz)
            await db.flush()

            for question_data in quiz_data.questions:
                if len(question_data.options) < 2:
                    raise HTTPException(
                        status_code=400,
                        detail="Each question must have at least two options.",
                    )

                new_question = QuestionModel(
                    text=question_data.text, quiz_id=new_quiz.id
                )
                db.add(new_question)
                await db.flush()

                for option_data in question_data.options:
                    new_option = OptionModel(
                        text=option_data.text,
                        is_correct=option_data.is_correct,
                        question_id=new_question.id,
                    )
                    db.add(new_option)
                    await db.flush()
            await db.refresh(new_quiz)
            await notification_service.notify_users(
                company_id=company_id,
                quiz_id=quiz_data.id,
                notification_text=notification_text,
                db=db,
            )
            await db.commit()
            return new_quiz
        except Exception as e:
            await db.rollback()
            raise e

    async def update(
        self, id_: int, db: AsyncSession, data: QuizCreateSchema, user_id: int
    ):
        count = 0
        for question in data.questions:
            count += 1
        if count < 2:
            raise HTTPException(
                detail="There must be two or more questions", status_code=403
            )
        quiz = await quiz_crud.get_one(id_=id_, db=db)
        member = await member_crud.get_one(id_=user_id, db=db)
        if quiz is None:
            raise HTTPException(detail="Quiz not found", status_code=404)
        company = await company_crud.get_one(id_=quiz.company_id, db=db)
        if company is None:
            raise HTTPException(detail="Company not found", status_code=404)
        if member is None or member.role != "admin":
            if user_id != company.owner_id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
        quiz.id = data.id
        quiz.name = data.name
        quiz.description = data.description
        questions = await question_crud.get_all_by_filter(
            filters={"quiz_id": id_}, db=db
        )
        await question_crud.delete_all_by_filters(filters={"quiz_id": id_}, db=db)
        for question in questions:
            await option_crud.delete_all_by_filters(
                filters={"question_id": question.id}, db=db
            )
        for question_data in data.questions:
            if len(question_data.options) < 2:
                raise HTTPException(
                    detail="There must be two or more options for every question",
                    status_code=403,
                )
            db_question = QuestionModel(text=question_data.text, quiz_id=quiz.id)
            db.add(db_question)
            await db.commit()
            await db.refresh(db_question)

            for option_data in question_data.options:
                db_option = OptionModel(
                    text=option_data.text,
                    is_correct=option_data.is_correct,
                    question_id=db_question.id,
                )
                db.add(db_option)
        await db.commit()
        return quiz


quiz_service = QuizService()
