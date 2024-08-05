from unittest.mock import patch, AsyncMock
import pytest
from fastapi import HTTPException
from app.db.models.models import (
    CompanyModel,
    MemberModel,
    QuizModel,
    QuestionModel,
)
from app.schemas.schemas import (
    QuizCreateSchema,
    QuestionCreateSchema,
    OptionCreateSchema,
)
from app.services.quiz_service import QuizService
from app.tests.conftest import get_db_fixture


@pytest.fixture
async def quiz_service():
    return QuizService()


@pytest.fixture
def valid_quiz_data():
    return QuizCreateSchema(
        id=1,
        name="Sample Quiz",
        description="A sample quiz",
        questions=[
            QuestionCreateSchema(
                text="Sample Question 1",
                options=[
                    OptionCreateSchema(text="Option 1", is_correct=True),
                    OptionCreateSchema(text="Option 2", is_correct=False),
                ],
            ),
            QuestionCreateSchema(
                text="Sample Question 2",
                options=[
                    OptionCreateSchema(text="Option 3", is_correct=False),
                    OptionCreateSchema(text="Option 4", is_correct=True),
                ],
            ),
        ],
    )


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.quiz_crud.quiz_crud.get_one")
async def test_create_quiz_success(
    mock_quiz_get_one,
    mock_member_get_one,
    mock_company_get_one,
    quiz_service,
    get_db_fixture,
    valid_quiz_data,
):
    mock_company_get_one.return_value = CompanyModel(id=1, owner_id=1)
    mock_member_get_one.return_value = MemberModel(id=1, role="admin")
    mock_quiz_get_one.side_effect = [
        None,
        AsyncMock(id=valid_quiz_data.id, description=valid_quiz_data.description),
    ]
    quiz_service = await quiz_service
    async for db_session in get_db_fixture:
        db_session.add = AsyncMock()
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()
        db_session.flush = AsyncMock()

        result = await quiz_service.create(
            db=db_session,
            quiz_data=valid_quiz_data,
            user_id=1,
            company_id=1,
            notification_text="Hello World",
        )

        assert result.name == valid_quiz_data.name
        assert result.description == valid_quiz_data.description

        expected_add_calls = (
            1
            + len(valid_quiz_data.questions)
            + sum(len(q.options) for q in valid_quiz_data.questions)
        )

        assert db_session.add.call_count == expected_add_calls
        assert db_session.commit.call_count == 1
        assert db_session.flush.call_count == 7


@pytest.mark.asyncio
@patch("app.CRUD.quiz_crud.quiz_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.question_crud.question_crud.get_all_by_filter")
@patch("app.CRUD.question_crud.question_crud.delete_all_by_filters")
@patch("app.CRUD.option_crud.option_crud.delete_all_by_filters")
async def test_update_quiz_success(
    mock_option_delete_all_by_filters,
    mock_question_delete_all_by_filters,
    mock_get_all_questions_by_filter,
    mock_get_one_member,
    mock_get_one_company,
    mock_get_one_quiz,
    get_db_fixture,
    quiz_service,
    valid_quiz_data,
):
    quiz_service = await quiz_service

    mock_get_one_quiz.return_value = QuizModel(
        id=1, name="Original Quiz", description="Original Description", company_id=1
    )
    mock_get_one_company.return_value = CompanyModel(
        id=1, owner_id=1, name="Test Company", description="Test Description"
    )
    mock_get_one_member.return_value = MemberModel(id=1, company_id=1, role="admin")
    mock_get_all_questions_by_filter.return_value = [
        QuestionModel(id=1, text="Original Question 1", quiz_id=1),
        QuestionModel(id=2, text="Original Question 2", quiz_id=1),
    ]

    async for db in get_db_fixture:
        result = await quiz_service.update(
            id_=1, db=db, data=valid_quiz_data, user_id=1
        )

        assert result.id == valid_quiz_data.id
        assert result.name == valid_quiz_data.name
        assert result.description == valid_quiz_data.description

        mock_get_one_quiz.assert_called_once_with(id_=1, db=db)
        mock_get_one_company.assert_called_once_with(id_=1, db=db)
        mock_get_one_member.assert_called_once_with(id_=1, db=db)
        mock_get_all_questions_by_filter.assert_called_once_with(
            filters={"quiz_id": 1}, db=db
        )
        mock_question_delete_all_by_filters.assert_called_once_with(
            filters={"quiz_id": 1}, db=db
        )
        assert mock_option_delete_all_by_filters.call_count == 2
        assert db.add.call_count == 6


@pytest.mark.asyncio
@patch("app.CRUD.quiz_crud.quiz_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_update_quiz_errors(
    mock_get_one_member,
    mock_get_one_company,
    mock_get_one_quiz,
    quiz_service,
    get_db_fixture,
    valid_quiz_data,
):
    quiz_service = await quiz_service

    invalid_quiz_data = QuizCreateSchema(
        id=1,
        name="Updated Quiz",
        description="Updated Description",
        questions=[
            QuestionCreateSchema(
                text="Updated Question 1",
                options=[
                    OptionCreateSchema(text="Option 1", is_correct=True),
                    OptionCreateSchema(text="Option 2", is_correct=False),
                ],
            )
        ],
    )

    async for db in get_db_fixture:
        mock_get_one_quiz.return_value = None
        mock_get_one_company.return_value = None
        mock_get_one_member.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await quiz_service.update(id_=1, db=db, data=invalid_quiz_data, user_id=1)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "There must be two or more questions"

        mock_get_one_quiz.return_value = None
        mock_get_one_company.return_value = None
        mock_get_one_member.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await quiz_service.update(id_=1, db=db, data=valid_quiz_data, user_id=1)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Quiz not found"

        mock_get_one_quiz.return_value = QuizModel(
            id=1, name="Original Quiz", description="Original Description", company_id=1
        )
        mock_get_one_company.return_value = None
        mock_get_one_member.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await quiz_service.update(id_=1, db=db, data=valid_quiz_data, user_id=1)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Company not found"

        mock_get_one_quiz.return_value = QuizModel(
            id=1, name="Original Quiz", description="Original Description", company_id=1
        )
        mock_get_one_company.return_value = CompanyModel(
            id=1, owner_id=2, name="Test Company", description="Test Description"
        )
        mock_get_one_member.return_value = MemberModel(
            id=1, company_id=1, role="member"
        )

        with pytest.raises(HTTPException) as exc_info:
            await quiz_service.update(id_=1, db=db, data=valid_quiz_data, user_id=1)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "You are not a member of this company."
