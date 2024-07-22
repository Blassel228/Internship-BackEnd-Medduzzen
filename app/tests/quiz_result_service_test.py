import pytest
from unittest.mock import patch
from app.schemas.schemas import QuizResultCreateInSchema
from app.db.models.models import (
    QuizModel,
    QuestionModel,
    OptionModel,
    CompanyModel,
    MemberModel,
    QuizResultModel,
    UserModel,
)
from app.services.quiz_result_service import QuizResultService


@pytest.fixture
async def quiz_result_service():
    return QuizResultService()


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_one")
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_one_by_filter")
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.add")
@patch("app.CRUD.quiz_crud.quiz_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.option_crud.option_crud.get_one")
@patch("app.services.redis_service.redis_service.cache_quiz_result")
@patch("app.CRUD.user_crud.user_crud.get_one")
async def test_pass_quiz_success(
    mock_get_one_user,
    mock_cache_quiz_result,
    mock_get_one_option,
    mock_get_one_member,
    mock_get_one_company,
    mock_get_one_quiz,
    mock_add_quiz_result,
    mock_get_one_quiz_result_by_filter,
    get_db_fixture,
    quiz_result_service,
):
    quiz_data = QuizResultCreateInSchema(id=1, quiz_id=1, options_ids=[1, 2])
    user_id = 1
    quiz_result_service = await quiz_result_service

    mock_get_one_user.return_value = UserModel(id=1, email="user@example.com")
    mock_get_one_quiz.return_value = QuizModel(
        id=1,
        company_id=1,
        name="Test Quiz",
        description="Test Description",
        questions=[
            QuestionModel(
                id=1,
                text="Question 1",
                options=[
                    OptionModel(id=1, text="Option 1", is_correct=True, question_id=1),
                    OptionModel(id=2, text="Option 2", is_correct=False, question_id=1),
                ],
            ),
            QuestionModel(
                id=2,
                text="Question 2",
                options=[
                    OptionModel(id=3, text="Option 3", is_correct=True, question_id=2),
                    OptionModel(id=4, text="Option 4", is_correct=False, question_id=2),
                ],
            ),
        ],
    )
    mock_get_one_company.return_value = CompanyModel(
        id=1, owner_id=1, name="Test Company", description="Test Description"
    )
    mock_get_one_member.return_value = MemberModel(id=1, company_id=1, role="member")
    mock_get_one_option.side_effect = [
        OptionModel(id=1, text="Option 1", is_correct=True, question_id=1),
        OptionModel(id=3, text="Option 3", is_correct=True, question_id=2),
    ]
    mock_get_one_quiz_result_by_filter.return_value = None
    mock_add_quiz_result.return_value = QuizResultModel(
        id=1, quiz_id=1, company_id=1, score=1.0, user_id=1
    )

    async for db in get_db_fixture:
        result = await quiz_result_service.pass_quiz(
            data=quiz_data, user_id=user_id, db=db
        )
        assert result.quiz_id == quiz_data.quiz_id
        assert result.user_id == user_id
        assert result.score == 1.0

        mock_get_one_quiz.assert_called_once_with(id_=quiz_data.quiz_id, db=db)
        mock_get_one_company.assert_called_once_with(id_=1, db=db)
        mock_get_one_member.assert_called_once_with(id_=user_id, db=db)
        assert mock_get_one_option.call_count == 2
        mock_add_quiz_result.assert_called_once()

        cached_data = {
            "quiz": {
                "id": 1,
                "name": "Test Quiz",
                "description": "Test Description",
            },
            "company": {
                "id": 1,
                "name": "Test Company",
                "description": "Test Description",
            },
            "user": {"id": 1, "email": "user@example.com"},
            "questions": {
                1: {"question_text": "Question 1"},
                2: {"question_text": "Question 2"},
            },
            "score": 1.0,
            "user_answers": {
                1: {
                    "question_text": "Question 1",
                    "provided_option_id": 1,
                    "is_correct": True,
                },
                2: {
                    "question_text": "Question 2",
                    "provided_option_id": 2,
                    "is_correct": False,
                },
            },
        }

        mock_cache_quiz_result.assert_called_once_with(data=cached_data)
