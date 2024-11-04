from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud
from app.CRUD.option_crud import option_crud
from app.CRUD.question_crud import question_crud
from app.CRUD.quiz_crud import quiz_crud
from app.db.models.option_model import OptionModel
from app.db.models.question_model import QuestionModel
from app.db.models.quiz_model import QuizModel
from app.schemas.schemas import (
    QuizCreateSchema,
    QuizGetSchema,
    QuestionGetSchema,
    OptionGetSchema,
)
from app.services.notification_service import notification_service
import pandas as pd
from app.exceptions.custom_exceptions import check_user_permissions


class QuizService:
    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        company_id: int,
        notification_text: str | None,
        quiz_data: QuizCreateSchema,
    ) -> QuizModel:
        try:
            quiz = await quiz_crud.get_one(id_=quiz_data.id, db=db)
            if quiz is not None:
                raise HTTPException(
                    status_code=409, detail="A quiz with such an id already exist"
                )
            company = await company_crud.get_one(id_=company_id, db=db)
            if company is None:
                raise HTTPException(
                    status_code=404, detail="Such a company does not exist"
                )
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
            await db.commit()
            await db.refresh(new_quiz)
            if notification_text:
                await notification_service.notify_users(
                    company_id=company_id,
                    quiz_id=quiz_data.id,
                    notification_text=notification_text,
                    db=db,
                )

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
                detail="There must be two or more questions", status_code=400
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
                    status_code=404, detail="You are not a member of this company."
                )
        quiz.id = data.id
        quiz.name = data.name
        quiz.description = data.description
        questions = await question_crud.get_all_by_filter(
            filters={"quiz_id": id_}, db=db
        )
        for question in questions:
            await option_crud.delete_all_by_filters(
                filters={"question_id": question.id}, db=db
            )
        await question_crud.delete_all_by_filters(filters={"quiz_id": id_}, db=db)

        for question_data in data.questions:
            if len(question_data.options) < 2:
                raise HTTPException(
                    detail="There must be two or more options for every question",
                    status_code=400,
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
        quiz = await quiz_crud.get_one(id_=data.id, db=db)
        return quiz

    async def parse_and_create_or_update_quiz_from_upload(
        self, company_id: int, file: UploadFile, db: AsyncSession, user_id: int
    ):
        company = await company_crud.get_one(id_=company_id, db=db)
        member = await member_crud.get_one(id_=user_id, db=db)
        check_user_permissions(user_id=user_id, company=company, member=member)
        excel_data = pd.read_excel(file.file, sheet_name=None)
        quiz_df = excel_data["Quiz"]
        questions_df = excel_data["Questions"]
        options_df = excel_data["Options"]

        quiz_name = quiz_df.at[0, "name"]
        quiz_description = quiz_df.at[0, "description"]

        quizzes = await quiz_crud.get_all(db=db)
        new_questions = questions_df["question_text"].tolist()

        found_matching_quiz = False
        quiz_to_update = None

        for quiz in quizzes:
            if quiz.name == quiz_name:
                found_matching_quiz = True
                quiz_to_update = quiz
                break

        if found_matching_quiz:
            quiz_to_update.description = quiz_description
            await db.flush()

            for question in quiz_to_update.questions:
                if question.text in new_questions:
                    question_options_df = options_df[
                        options_df["question_text"] == question.text
                    ]
                    existing_option_texts = {option.text for option in question.options}

                    for _, option_row in question_options_df.iterrows():
                        option_text = str(option_row["option_text"])
                        is_correct = bool(option_row["is_correct"])

                        if option_text not in existing_option_texts:
                            new_option = OptionModel(
                                text=option_text,
                                is_correct=is_correct,
                                question_id=question.id,
                            )
                            db.add(new_option)
                        else:
                            for option in question.options:
                                if option.text == option_text:
                                    option.is_correct = is_correct

                    for option in question.options:
                        if option.text not in question_options_df["option_text"].values:
                            await db.delete(option)

        else:
            quiz_to_update = QuizModel(
                company_id=company_id,
                name=quiz_name,
                description=quiz_description,
            )
            db.add(quiz_to_update)

            await db.flush()

            for _, question_row in questions_df.iterrows():
                question_text = question_row["question_text"]
                new_question = QuestionModel(
                    text=question_text, quiz_id=quiz_to_update.id
                )
                db.add(new_question)

                await db.flush()

                question_options_df = options_df[
                    options_df["question_text"] == question_text
                ]
                for _, option_row in question_options_df.iterrows():
                    option_text = str(option_row["option_text"])
                    is_correct = bool(option_row["is_correct"])
                    new_option = OptionModel(
                        text=option_text,
                        is_correct=is_correct,
                        question_id=new_question.id,
                    )
                    db.add(new_option)

        await db.commit()

        quiz = await quiz_crud.get_one(id_=quiz_to_update.id, db=db)

        quiz_response = QuizGetSchema(
            id=quiz.id,
            name=quiz.name,
            description=quiz.description,
            questions=[
                QuestionGetSchema(
                    text=question.text,
                    options=[
                        OptionGetSchema(text=option.text, is_correct=option.is_correct)
                        for option in question.options
                    ],
                )
                for question in quiz.questions
            ]
            if quiz.questions
            else None,
        )

        return quiz_response

    async def export_single_quiz_to_excel(self, db: AsyncSession, id_: int):
        quiz = await quiz_crud.get_one(id_=id_, db=db)

        if not quiz:
            raise HTTPException(status_code=404, detail="Not Found")

        quiz_data = QuizGetSchema(
            quiz_id=quiz.id,
            company_id=quiz.company_id,
            name=quiz.name,
            description=quiz.description,
            pass_count=quiz.pass_count,
            registration_date=quiz.registration_date,
            questions=[
                QuestionGetSchema(
                    question_id=question.id,
                    quiz_id=question.quiz_id,
                    text=question.text,
                    options=[
                        OptionGetSchema(
                            option_id=option.id,
                            question_id=option.question_id,
                            text=option.text,
                            is_correct=option.is_correct,
                        )
                        for option in question.options
                    ],
                )
                for question in quiz.questions
            ],
        )

        # Convert data into DataFrames
        quiz_data_dict = [quiz_data.dict(exclude={"questions"})]
        question_data_dict = [q.dict(exclude={"options"}) for q in quiz_data.questions]
        option_data_dict = [
            o.dict() for question in quiz_data.questions for o in question.options
        ]

        quiz_df = pd.DataFrame(quiz_data_dict)
        question_df = pd.DataFrame(question_data_dict)
        option_df = pd.DataFrame(option_data_dict)


        file_path = Path("quiz_export.xlsx")
        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            quiz_df.to_excel(writer, sheet_name="Quiz", index=False)
            question_df.to_excel(writer, sheet_name="Questions", index=False)
            option_df.to_excel(writer, sheet_name="Options", index=False)

        return file_path

quiz_service = QuizService()
