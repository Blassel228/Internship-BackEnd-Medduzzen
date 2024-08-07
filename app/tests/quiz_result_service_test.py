from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.db.models.quiz_result_model import QuizResultModel
from app.db.models.option_model import OptionModel
from app.db.models.question_model import QuestionModel
from app.db.models.quiz_model import QuizModel
from app.db.models.member_model import MemberModel
from app.db.models.company_model import CompanyModel
from app.db.models.user_model import UserModel
from app.schemas.schemas import QuizResultCreateInSchema, QuizResultCreateSchema
from app.services.quiz_result_service import QuizResultService


@pytest.fixture
async def quiz_result_service():
    return QuizResultService()


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter")
async def test_user_get_its_result_success(
    mock_get_all_by_filter, quiz_result_service, get_db_fixture
):
    quiz_result_service = await quiz_result_service
    user_id = 1

    async for db_session in get_db_fixture:
        mock_results = [
            QuizResultModel(id=1, user_id=user_id, score=85),
            QuizResultModel(id=2, user_id=user_id, score=90),
        ]
        mock_get_all_by_filter.return_value = mock_results

        result = await quiz_result_service.user_get_its_result(
            user_id=user_id, db=db_session
        )

        assert result == mock_results
        mock_get_all_by_filter.assert_awaited_once_with(
            db=db_session, filters={"user_id": user_id}
        )


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
async def test_get_all_company_results_success(
    mock_get_company,
    mock_get_member,
    mock_get_results,
    quiz_result_service,
    get_db_fixture,
):
    quiz_result_service = await quiz_result_service
    mock_get_company.return_value = CompanyModel(
        id=1, owner_id=1, name="Test Company", description="Test Description"
    )
    mock_get_member.return_value = MemberModel(id=1, company_id=1, role="admin")
    mock_get_results.return_value = [
        QuizResultCreateSchema(id=1, quiz_id=1, company_id=1, score=0.9, user_id=1),
        QuizResultCreateSchema(id=2, quiz_id=1, company_id=1, score=0.8, user_id=2),
    ]

    async for db in get_db_fixture:
        results = await quiz_result_service.get_all_company_results(
            user_id=1, company_id=1, db=db
        )
        assert len(results) == 2
        assert results[0].id == 1
        assert results[1].id == 2

        mock_get_company.assert_called_once_with(id_=1, db=db)
        mock_get_member.assert_called_once_with(id_=1, db=db)
        mock_get_results.assert_called_once_with(db=db, filters={"company_id": 1})


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
async def test_get_all_company_results_errors(
    mock_get_company,
    mock_get_member,
    mock_get_results,
    quiz_result_service,
    get_db_fixture,
):
    quiz_result_service = await quiz_result_service
    mock_get_company.return_value = None
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await quiz_result_service.get_all_company_results(
                user_id=1, company_id=1, db=db
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "There is no such a company"
    mock_get_company.reset_mock()

    mock_get_company.return_value = CompanyModel(
        id=1, owner_id=2, name="Test Company", description="Test Description"
    )
    mock_get_member.return_value = None
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await quiz_result_service.get_all_company_results(
                user_id=1, company_id=1, db=db
            )
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "You have no right to get all users results"
    mock_get_company.reset_mock()
    mock_get_member.reset_mock()

    mock_get_company.return_value = CompanyModel(
        id=1, owner_id=1, name="Test Company", description="Test Description"
    )
    mock_get_member.return_value = MemberModel(id=1, company_id=1, role="member")
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await quiz_result_service.get_all_company_results(
                user_id=1, company_id=1, db=db
            )
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "You do not have such rights"
    mock_get_company.reset_mock()
    mock_get_member.reset_mock()

    mock_get_company.return_value = CompanyModel(
        id=1, owner_id=1, name="Test Company", description="Test Description"
    )
    mock_get_member.return_value = MemberModel(id=2, company_id=2, role="admin")
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await quiz_result_service.get_all_company_results(
                user_id=1, company_id=1, db=db
            )
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "You are not a member of the company"
    mock_get_company.reset_mock()
    mock_get_member.reset_mock()
    mock_get_results.reset_mock()


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_get_results_for_user_success(
    mock_get_one_member,
    mock_get_one_company,
    mock_get_all_by_filter,
    get_db_fixture,
    quiz_result_service,
):
    user_id = 1
    company_id = 1
    result_id = 1
    quiz_result_service = await quiz_result_service
    quiz_results = [
        QuizResultModel(
            id=1, quiz_id=1, company_id=company_id, score=0.75, user_id=user_id
        )
    ]

    mock_get_one_company.return_value = CompanyModel(
        id=company_id, owner_id=user_id, name="Test Company"
    )
    mock_get_one_member.return_value = MemberModel(
        id=user_id, company_id=company_id, role="admin"
    )
    mock_get_all_by_filter.return_value = quiz_results

    async for db in get_db_fixture:
        results = await quiz_result_service.get_results_for_user(
            user_id=user_id, id_=result_id, company_id=company_id, db=db
        )

        assert results == quiz_results
        assert len(results) == 1
        assert results[0].id == 1
        assert results[0].quiz_id == 1
        assert results[0].company_id == company_id
        assert results[0].score == 0.75
        assert results[0].user_id == user_id

        mock_get_one_company.assert_called_once_with(id_=company_id, db=db)
        mock_get_one_member.assert_called_once_with(id_=user_id, db=db)
        mock_get_all_by_filter.assert_called_once_with(
            db=db, filters={"user_id": result_id}
        )


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_get_results_for_user_error(
    mock_get_one_member,
    mock_get_one_company,
    mock_get_all_by_filter,
    get_db_fixture,
    quiz_result_service,
):
    user_id = 1
    company_id = 1
    result_id = 1
    quiz_results = [
        QuizResultModel(
            id=1, quiz_id=1, company_id=company_id, score=0.75, user_id=user_id
        )
    ]
    quiz_result_service = await quiz_result_service

    mock_get_one_company.return_value = None
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.get_results_for_user(
                user_id=user_id, id_=result_id, company_id=company_id, db=db
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "There is no such a company"

    mock_get_one_company.return_value = CompanyModel(
        id=company_id, owner_id=user_id, name="Test Company"
    )

    mock_get_one_member.return_value = None
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.get_results_for_user(
                user_id=user_id, id_=result_id, company_id=company_id, db=db
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You have no right to get all users results"

    mock_get_one_member.return_value = MemberModel(
        id=user_id, company_id=company_id, role="member"
    )

    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.get_results_for_user(
                user_id=user_id, id_=result_id, company_id=company_id, db=db
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You do not have such rights"

    mock_get_one_member.return_value = MemberModel(
        id=user_id, company_id=company_id, role="admin"
    )

    mock_get_one_member.return_value = MemberModel(
        id=user_id, company_id=2, role="admin"
    )
    async for db in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.get_results_for_user(
                user_id=user_id, id_=result_id, company_id=company_id, db=db
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You are not a member of the company"

    mock_get_one_member.return_value = MemberModel(
        id=user_id, company_id=company_id, role="admin"
    )

    mock_get_all_by_filter.return_value = quiz_results
    async for db in get_db_fixture:
        results = await quiz_result_service.get_results_for_user(
            user_id=user_id, id_=result_id, company_id=company_id, db=db
        )
        assert results == quiz_results

        mock_get_all_by_filter.assert_called_once_with(
            db=db, filters={"user_id": result_id}
        )


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


@pytest.mark.asyncio
@patch("app.CRUD.quiz_result_crud.quiz_result_crud.get_one")
@patch("app.CRUD.quiz_crud.quiz_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.option_crud.option_crud.get_one")
async def test_pass_quiz_errors(
    mock_get_one_option,
    mock_get_one_member,
    mock_get_one_company,
    mock_get_one_quiz,
    mock_get_one_quiz_result,
    get_db_fixture,
    quiz_result_service,
):
    quiz_data = QuizResultCreateInSchema(id=1, quiz_id=1, options_ids=[1, 2])
    quiz_result_service = await quiz_result_service

    async for db in get_db_fixture:
        # Test case: Result with such an id already exists
        mock_get_one_quiz_result.return_value = QuizResultModel(id=1)
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.pass_quiz(data=quiz_data, user_id=1, db=db)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Result with such an id already exists"

        # Reset mock
        mock_get_one_quiz_result.return_value = None

        # Test case: No such quiz
        mock_get_one_quiz.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.pass_quiz(data=quiz_data, user_id=1, db=db)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "There is no such a quiz"

        # Set up for the next test cases
        mock_get_one_quiz.return_value = QuizModel(
            id=1,
            company_id=1,
            name="Test Quiz",
            description="Test Description",
            questions=[
                QuestionModel(id=1, text="Question 1", options=[]),
            ],
        )
        mock_get_one_member.return_value = None
        mock_get_one_company.return_value = CompanyModel(
            id=1, owner_id=2, name="Test Company"  # Owner ID different from user_id
        )

        # Test case: User is not a member of the company
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.pass_quiz(data=quiz_data, user_id=1, db=db)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You are not a member of that company"

        # Update member mock
        mock_get_one_member.return_value = MemberModel(
            id=1, company_id=1, role="member"
        )

        # Test case: Invalid number of options provided
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.pass_quiz(data=quiz_data, user_id=1, db=db)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Invalid number of options provided"

        # Set up for the next test cases
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
                        OptionModel(
                            id=1, text="Option 1", is_correct=True, question_id=1
                        ),
                        OptionModel(
                            id=3, text="Option 3", is_correct=True, question_id=1
                        ),
                    ],
                ),
                QuestionModel(
                    id=2,
                    text="Question 2",
                    options=[
                        OptionModel(
                            id=4, text="Option 1", is_correct=True, question_id=2
                        ),
                        OptionModel(
                            id=5, text="Option 3", is_correct=True, question_id=2
                        ),
                    ],
                ),
            ],
        )

        # Test case: No such option
        mock_get_one_option.side_effect = [
            OptionModel(id=1, text="Option 1", is_correct=True, question_id=1),
            None,
        ]
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.pass_quiz(data=quiz_data, user_id=1, db=db)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "There is no such an option with id 2"

        mock_get_one_option.side_effect = [
            OptionModel(id=1, text="Option 1", is_correct=True, question_id=1),
            OptionModel(id=2, text="Option 2", is_correct=False, question_id=1),
        ]
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.pass_quiz(data=quiz_data, user_id=1, db=db)
        assert exc_info.value.status_code == 403
        assert (
            exc_info.value.detail == "Option provided do not comply with the question"
        )


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
async def test_get_average_score_for_company(
    mock_get_one, get_db_fixture, quiz_result_service
):
    quiz_result_service = await quiz_result_service
    company_id = 1
    mock_get_one.return_value = {"id": company_id}

    mock_db_result = [(1, 80.0), (2, 90.0)]

    async def mock_execute(stmt):
        class MockResult:
            def __init__(self, result):
                self.result = result

            def iterator(self):
                return iter(self.result)

        return MockResult(mock_db_result)

    async for session in get_db_fixture:
        session.execute.side_effect = mock_execute
        result = await quiz_result_service.get_average_score_for_company(
            db=session, company_id=company_id
        )
        result_list = list(result())
        assert result_list == mock_db_result
        mock_get_one.assert_called_once_with(id_=company_id, db=session)


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
async def test_get_average_score_for_company_not_found(
    mock_get_one, quiz_result_service, get_db_fixture
):
    quiz_result_service = await quiz_result_service
    company_id = 1

    mock_get_one.return_value = None

    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await quiz_result_service.get_average_score_for_company(
                db=db_session, company_id=company_id
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Such a company does not exist"

        mock_get_one.assert_awaited_once_with(id_=company_id, db=db_session)
