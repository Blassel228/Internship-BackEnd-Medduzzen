import datetime
from unittest.mock import patch, AsyncMock
import pytest
from fastapi import HTTPException
from app.db.models.notification_model import NotificationModel
from app.db.models.quiz_result_model import QuizResultModel
from app.db.models.quiz_model import QuizModel
from app.db.models.member_model import MemberModel
from app.db.models.company_model import CompanyModel
from app.schemas.schemas import NotificationCreateSchema
from app.services.notification_service import NotificationService


@pytest.fixture
async def notification_service():
    return NotificationService()


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one", new_callable=AsyncMock)
@patch("app.CRUD.notification_crud.notification_crud.add", new_callable=AsyncMock)
async def test_notify_users_success(
    mock_add, mock_get_one, notification_service, get_db_fixture
):
    notification_service = await notification_service
    mock_company_data = CompanyModel(
        id=1, members=[MemberModel(id=2, company_id=1), MemberModel(id=3, company_id=1)]
    )
    mock_get_one.return_value = mock_company_data

    notification_data = NotificationCreateSchema(
        user_id=2, quiz_id=123, text="Test Notification"
    )

    async for session in get_db_fixture:
        await notification_service.notify_users(
            quiz_id=notification_data.quiz_id,
            company_id=mock_company_data.id,
            notification_text=notification_data.text,
            db=session,
        )

        assert mock_add.call_count == len(mock_company_data.members)
        for member in mock_company_data.members:
            mock_add.assert_any_call(
                data=NotificationCreateSchema(
                    user_id=member.id,
                    quiz_id=notification_data.quiz_id,
                    text=notification_data.text,
                ),
                db=session,
            )


@pytest.mark.asyncio
@patch("app.services.notification_service.quiz_crud.get_one")
@patch("app.services.notification_service.company_crud.get_one")
async def test_notify_users_errors(
    mock_company_get_one, mock_quiz_get_one, notification_service, get_db_fixture
):
    notification_service = await notification_service
    mock_quiz_get_one.return_value = None
    mock_company_get_one.return_value = CompanyModel(
        id=1, members=[MemberModel(id=2, company_id=1)]
    )

    async for session in get_db_fixture:
        with pytest.raises(HTTPException, match="Such a quiz does not exist"):
            await notification_service.notify_users(
                quiz_id=1,
                company_id=1,
                notification_text="Test Notification",
                db=session,
            )

    mock_quiz_get_one.reset_mock()
    mock_company_get_one.reset_mock()

    mock_quiz_get_one.return_value = AsyncMock(id=1, description="Sample Quiz")
    mock_company_get_one.return_value = None

    async for session in get_db_fixture:
        with pytest.raises(HTTPException, match="Such a company does not exist"):
            await notification_service.notify_users(
                quiz_id=1,
                company_id=1,
                notification_text="Test Notification",
                db=session,
            )


@pytest.mark.asyncio
@patch("app.services.notification_service.notification_crud.get_one")
async def test_mark_as_read_success(mock_get_one, notification_service, get_db_fixture):
    notification_service = await notification_service
    mock_notification = NotificationModel(id=1, user_id=1, is_read=False)
    mock_get_one.return_value = mock_notification

    async for session in get_db_fixture:
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        result = await notification_service.mark_as_read(id_=1, user_id=1, db=session)

        assert result.is_read is True
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
@patch("app.services.notification_service.notification_crud.get_one")
async def test_mark_as_read_errors(mock_get_one, notification_service, get_db_fixture):
    notification_service = await notification_service
    async for session in get_db_fixture:
        mock_get_one.return_value = None
        with pytest.raises(HTTPException, match="Was not found"):
            await notification_service.mark_as_read(id_=1, user_id=1, db=session)

        mock_get_one.reset_mock()
        mock_notification = NotificationModel(id=1, user_id=2, is_read=False)
        mock_get_one.return_value = mock_notification
        with pytest.raises(HTTPException, match="The notification was not sent to you"):
            await notification_service.mark_as_read(id_=1, user_id=1, db=session)


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_all", new_callable=AsyncMock)
@patch("app.CRUD.quiz_crud.quiz_crud.get_all", new_callable=AsyncMock)
@patch(
    "app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter",
    new_callable=AsyncMock,
)
@patch("app.CRUD.notification_crud.notification_crud.add", new_callable=AsyncMock)
async def test_pass_check(
    mock_add_notification,
    mock_get_all_by_filter,
    mock_get_all_quizzes,
    mock_get_all_members,
    notification_service,
    get_db_fixture,
):
    notification_service = await notification_service

    mock_members = [MemberModel(id=1, company_id=1), MemberModel(id=2, company_id=1)]
    mock_get_all_members.return_value = mock_members

    mock_quizzes = [QuizModel(id=1), QuizModel(id=2)]
    mock_get_all_quizzes.return_value = mock_quizzes

    mock_quiz_results = [
        QuizResultModel(
            id=1,
            quiz_id=1,
            user_id=1,
            registration_date=datetime.datetime.utcnow() - datetime.timedelta(hours=23),
        ),  # Within 24 hours
        QuizResultModel(
            id=2,
            quiz_id=2,
            user_id=2,
            registration_date=datetime.datetime.utcnow() - datetime.timedelta(hours=26),
        ),  # Older than 24 hours
    ]
    mock_get_all_by_filter.side_effect = lambda filters, db: [
        result
        for result in mock_quiz_results
        if result.quiz_id == filters["quiz_id"] and result.user_id == filters["user_id"]
    ]

    async for session in get_db_fixture:
        session.commit = AsyncMock()

        text = "Time to take the quiz again!"
        notifications = await notification_service.pass_check(text=text, db=session)

        assert len(notifications) == 3

        for quiz in mock_quizzes:
            for member in mock_members:
                recent_result = [
                    result
                    for result in mock_quiz_results
                    if result.quiz_id == quiz.id
                    and result.user_id == member.id
                    and result.registration_date
                    > datetime.datetime.utcnow() - datetime.timedelta(hours=24)
                ]
                if not recent_result:
                    mock_add_notification.assert_any_call(
                        data=NotificationCreateSchema(
                            quiz_id=quiz.id, user_id=member.id, text=text
                        ),
                        db=session,
                    )
        session.commit.assert_awaited()


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_all", new_callable=AsyncMock)
@patch("app.CRUD.quiz_crud.quiz_crud.get_all", new_callable=AsyncMock)
@patch(
    "app.CRUD.quiz_result_crud.quiz_result_crud.get_all_by_filter",
    new_callable=AsyncMock,
)
@patch("app.CRUD.notification_crud.notification_crud.add", new_callable=AsyncMock)
async def test_pass_check_error_handling(
    mock_add_notification,
    mock_get_all_by_filter,
    mock_get_all_quizzes,
    mock_get_all_members,
    notification_service,
    get_db_fixture,
):
    notification_service = await notification_service

    mock_members = [MemberModel(id=1, company_id=1), MemberModel(id=2, company_id=1)]
    mock_get_all_members.return_value = mock_members

    mock_quizzes = [QuizModel(id=1), QuizModel(id=2)]
    mock_get_all_quizzes.return_value = mock_quizzes

    mock_quiz_results = [
        QuizResultModel(
            id=1,
            quiz_id=1,
            user_id=1,
            registration_date=datetime.datetime.utcnow() - datetime.timedelta(hours=25),
        ),
        QuizResultModel(
            id=2,
            quiz_id=2,
            user_id=2,
            registration_date=datetime.datetime.utcnow() - datetime.timedelta(hours=26),
        ),
    ]
    mock_get_all_by_filter.side_effect = lambda filters, db: [
        result
        for result in mock_quiz_results
        if result.quiz_id == filters["quiz_id"] and result.user_id == filters["user_id"]
    ]

    mock_add_notification.side_effect = Exception("Failed to add notification")

    async for session in get_db_fixture:
        session.commit = AsyncMock()

        text = "Time to take the quiz again!"

        try:
            notifications = await notification_service.pass_check(text=text, db=session)
        except Exception as e:
            print(f"Caught an exception: {e}")

        mock_add_notification.assert_awaited()
        assert mock_add_notification.call_count > 0
        session.commit.assert_not_awaited()
