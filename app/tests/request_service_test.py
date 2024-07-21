from unittest.mock import patch
from fastapi import HTTPException
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
