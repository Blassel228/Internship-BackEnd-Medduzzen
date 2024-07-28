from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.schemas.schemas import RequestCreateInSchema, MemberCreateSchema
from app.services.request_service import RequestService
from app.db.models.models import CompanyModel, RequestModel
from app.tests.conftest import get_db_fixture
import pytest


@pytest.fixture
async def request_service():
    return RequestService()


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.request_crud.request_crud.get_all_by_filter")
async def test_owner_get_all_requests_success(
    mock_get_all_by_filter, mock_get_one_company, request_service, get_db_fixture
):
    user_id = 1
    company_id = 1
    mock_company = CompanyModel(
        id=company_id,
        owner_id=user_id,
        name="Company",
        description="Description",
        visible=True,
    )
    mock_requests = [
        RequestModel(id=1, company_id=company_id, sender_id=2),
        RequestModel(id=2, company_id=company_id, sender_id=3),
    ]

    mock_get_one_company.return_value = mock_company
    mock_get_all_by_filter.return_value = mock_requests
    request_service = await request_service
    async for db_session in get_db_fixture:
        result = await request_service.owner_get_all_requests(
            user_id=user_id, company_id=company_id, db=db_session
        )
        assert result == mock_requests
        mock_get_one_company.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_all_by_filter.assert_called_once_with(
            filters={"company_id": company_id}, db=db_session
        )


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.request_crud.request_crud.get_all_by_filter")
async def test_owner_get_all_requests_errors(
    mock_get_all_by_filter, mock_get_one_company, request_service, get_db_fixture
):
    user_id = 1
    company_id = 1
    mock_get_one_company.return_value = None
    request_service = await request_service
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await request_service.owner_get_all_requests(
                user_id=user_id, company_id=company_id, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Such a company does not exist"
        mock_get_one_company.assert_called_once_with(id_=company_id, db=db_session)
    mock_get_one_company.reset_mock()
    mock_company = CompanyModel(
        id=company_id,
        owner_id=2,
        name="Company",
        description="Description",
        visible=True,
    )
    mock_get_one_company.return_value = mock_company
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await request_service.owner_get_all_requests(
                user_id=user_id, company_id=company_id, db=db_session
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You do not own the company to get the requests"
        mock_get_one_company.assert_called_once_with(id_=company_id, db=db_session)
    mock_get_one_company.reset_mock()
    mock_get_all_by_filter.reset_mock()
    mock_company = CompanyModel(
        id=company_id,
        owner_id=user_id,
        name="Company",
        description="Description",
        visible=True,
    )
    mock_requests = [
        RequestModel(id=1, company_id=company_id, sender_id=2),
        RequestModel(id=2, company_id=company_id, sender_id=3),
    ]
    mock_get_one_company.return_value = mock_company
    mock_get_all_by_filter.return_value = mock_requests

    async for db_session in get_db_fixture:
        result = await request_service.owner_get_all_requests(
            user_id=user_id, company_id=company_id, db=db_session
        )
        assert result == mock_requests
        mock_get_one_company.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_all_by_filter.assert_called_once_with(
            filter={"company_id": company_id}
        )


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.request_crud.request_crud.get_one_by_filter")
async def test_send_request_success(
    mock_get_one_by_filter,
    mock_get_company,
    mock_get_member,
    request_service,
    get_db_fixture,
):
    mock_get_member.return_value = None
    mock_get_company.return_value = CompanyModel(id=1, owner_id=2)
    mock_get_one_by_filter.return_value = None

    request_service = await request_service

    request_payload = RequestCreateInSchema(
        id=1, company_id=1, request_text="I want to join"
    )

    async for db_session in get_db_fixture:
        response = await request_service.send_request(
            user_id=3, request=request_payload, db=db_session
        )
        assert response.sender_id == 3
        assert response.company_id == 1
        assert response.id == 1
        assert response.request_text == "I want to join"


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.request_crud.request_crud.get_one_by_filter")
async def test_send_request_errors(
    mock_get_one_by_filter,
    mock_get_company,
    mock_get_member,
    request_service,
    get_db_fixture,
):
    request_service = await request_service

    request_payload = RequestCreateInSchema(
        id=1, company_id=1, request_text="I want to join"
    )

    mock_get_member.return_value = MagicMock()
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await request_service.send_request(
                user_id=3, request=request_payload, db=db_session
            )
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "You are in a company already"

    mock_get_member.reset_mock()
    mock_get_company.reset_mock()

    mock_get_member.return_value = None
    mock_get_company.return_value = None
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await request_service.send_request(
                user_id=3, request=request_payload, db=db_session
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Such a company does not exist"

    mock_get_company.reset_mock()
    mock_get_company.return_value = CompanyModel(id=1, owner_id=3)
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await request_service.send_request(
                user_id=3, request=request_payload, db=db_session
            )
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "You cannot send request to company you own"

    mock_get_company.reset_mock()
    mock_get_one_by_filter.reset_mock()

    mock_get_company.return_value = MagicMock(id=1, owner_id=2)
    mock_get_one_by_filter.return_value = MagicMock()
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as excinfo:
            await request_service.send_request(
                user_id=3, request=request_payload, db=db_session
            )
        assert excinfo.value.status_code == 409
        assert excinfo.value.detail == "You have already sent request to that company"


@pytest.mark.asyncio
@patch("app.CRUD.request_crud.request_crud.get_one")
@patch("app.CRUD.user_crud.user_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one_by_filter")
@patch("app.CRUD.request_crud.request_crud.delete")
@patch("app.CRUD.member_crud.member_crud.add")
async def test_accept_request_success(
    mock_add_member,
    mock_delete_request,
    mock_get_company,
    mock_get_user,
    mock_get_request,
    request_service,
    get_db_fixture,
):
    request_id = 1
    user_id = 2
    request_sender_id = 3
    company_id = 1

    mock_get_request.return_value = MagicMock(
        id=request_id, sender_id=request_sender_id
    )
    mock_get_user.return_value = MagicMock(id=request_sender_id)
    mock_get_company.return_value = MagicMock(id=company_id, owner_id=user_id)

    request_service = await request_service
    expected_member = MemberCreateSchema(id=request_sender_id, company_id=company_id)
    mock_add_member.return_value = expected_member

    async for db_session in get_db_fixture:
        member = await request_service.accept_request(
            id_=request_id, user_id=user_id, db=db_session
        )
        assert member.id == request_sender_id
        assert member.company_id == company_id
        mock_get_request.assert_called_once_with(id_=request_id, db=db_session)
        mock_get_user.assert_called_once_with(id_=request_sender_id, db=db_session)
        mock_get_company.assert_called_once_with(
            db=db_session, filters={"owner_id": user_id}
        )
        mock_delete_request.assert_called_once_with(id_=request_id, db=db_session)
        mock_add_member.assert_called_once_with(db=db_session, data=expected_member)


@pytest.mark.asyncio
@patch("app.CRUD.request_crud.request_crud.get_one")
@patch("app.CRUD.user_crud.user_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one_by_filter")
async def test_accept_request_errors(
    mock_get_company, mock_get_user, mock_get_request, request_service, get_db_fixture
):
    request_id = 1
    user_id = 2
    request_sender_id = 3
    company_id = 1

    request_service = await request_service

    async for db_session in get_db_fixture:
        mock_get_request.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            await request_service.accept_request(
                id_=request_id, user_id=user_id, db=db_session
            )
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "The request with such an id does not exist"

        mock_get_request.reset_mock()
        mock_get_user.reset_mock()
        mock_get_company.reset_mock()

        mock_get_request.return_value = MagicMock(
            id=request_id, sender_id=request_sender_id
        )
        mock_get_user.return_value = MagicMock(id=request_sender_id)
        mock_get_company.return_value = MagicMock(id=company_id, owner_id=user_id + 1)

        with pytest.raises(HTTPException) as excinfo:
            await request_service.accept_request(
                id_=request_id, user_id=user_id, db=db_session
            )
        assert excinfo.value.status_code == 403
        assert (
            excinfo.value.detail
            == "You can not accept the request as you are not the owner"
        )
