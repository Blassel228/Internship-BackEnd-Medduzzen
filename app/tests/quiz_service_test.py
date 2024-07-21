import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.db.models.models import CompanyModel, MemberModel, QuizModel, QuestionModel, OptionModel
from app.schemas.schemas import QuizCreateSchema, QuestionCreateSchema, OptionCreateSchema
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
                    OptionCreateSchema(text="Option 2", is_correct=False)
                ]
            ),
            QuestionCreateSchema(
                text="Sample Question 2",
                options=[
                    OptionCreateSchema(text="Option 3", is_correct=False),
                    OptionCreateSchema(text="Option 4", is_correct=True)
                ]
            )
        ]
    )


@pytest.mark.asyncio
@patch('app.CRUD.company_crud.company_crud.get_one')
@patch('app.CRUD.member_crud.member_crud.get_one')
async def test_create_quiz_success(mock_member_get_one, mock_company_get_one, quiz_service, get_db_fixture,
                                   valid_quiz_data):
    mock_company_get_one.return_value = CompanyModel(id=1, owner_id=1)
    mock_member_get_one.return_value = MemberModel(id=1, role="admin")

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
            company_id=1
        )

        assert result.name == valid_quiz_data.name
        assert result.description == valid_quiz_data.description

        expected_add_calls = 1 + len(valid_quiz_data.questions) + sum(len(q.options) for q in valid_quiz_data.questions)

        assert db_session.add.call_count == expected_add_calls
        assert db_session.commit.call_count == 1
        assert db_session.flush.call_count == 4