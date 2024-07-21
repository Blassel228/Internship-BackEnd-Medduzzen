import pytest
from unittest.mock import patch
from app.services.member_service import MemberService
from app.db.models.models import CompanyModel, MemberModel
from fastapi import HTTPException
from app.tests.conftest import get_db_fixture


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_demote_member_from_admin_success(
    mock_get_member, mock_get_company, get_db_fixture
):
    user_id = 1
    member_id = 2
    company_id = 1
    mock_company = CompanyModel(id=company_id, owner_id=user_id)
    mock_member = MemberModel(id=member_id, company_id=company_id, role="admin")
    mock_get_company.return_value = mock_company
    mock_get_member.return_value = mock_member
    service = MemberService()
    async for db_session in get_db_fixture:
        result = await service.demote_member_from_admin(
            user_id=user_id, member_id=member_id, company_id=company_id, db=db_session
        )
        assert result.role == "member"
        mock_get_company.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_member.assert_called_once_with(id_=member_id, db=db_session)


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_demote_member_from_admin_errors(
    mock_get_member, mock_get_company, get_db_fixture
):
    user_id = 1
    member_id = 2
    company_id = 1
    mock_get_company.return_value = None  # Company not found

    service = MemberService()
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.demote_member_from_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Company not found"

    mock_get_company.return_value = CompanyModel(
        id=company_id, owner_id=999
    )  # Not the owner

    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.demote_member_from_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You do not own the company"

    mock_get_company.return_value = CompanyModel(id=company_id, owner_id=user_id)
    mock_get_member.return_value = None

    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.demote_member_from_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Member not found in this company"


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_promote_member_to_admin_success(
    mock_get_member, mock_get_company, get_db_fixture
):
    user_id = 1
    member_id = 2
    company_id = 1
    mock_company = CompanyModel(id=company_id, owner_id=user_id)
    mock_member = MemberModel(id=member_id, company_id=company_id, role="member")
    mock_get_company.return_value = mock_company
    mock_get_member.return_value = mock_member

    service = MemberService()
    async for db_session in get_db_fixture:
        result = await service.promote_member_to_admin(
            user_id=user_id, member_id=member_id, company_id=company_id, db=db_session
        )
        assert result.role == "admin"
        mock_get_company.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_member.assert_called_once_with(id_=member_id, db=db_session)


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_promote_member_to_admin_errors(
    mock_get_member, mock_get_company, get_db_fixture
):
    user_id = 1
    member_id = 2
    company_id = 1
    service = MemberService()
    mock_get_company.return_value = None
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.promote_member_to_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Company not found"

    mock_get_company.return_value = CompanyModel(id=company_id, owner_id=999)
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.promote_member_to_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You do not own the company"

    mock_get_company.return_value = CompanyModel(id=company_id, owner_id=user_id)
    mock_get_member.return_value = None
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.promote_member_to_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Member not found in this company"

    mock_member = MemberModel(id=member_id, company_id=company_id + 1, role="member")
    mock_get_member.return_value = mock_member
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await service.promote_member_to_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Member not found in this company"