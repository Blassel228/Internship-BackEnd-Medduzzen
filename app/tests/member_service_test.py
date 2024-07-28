import pytest
from unittest.mock import patch, AsyncMock
from app.services.member_service import MemberService
from app.db.models.models import CompanyModel, MemberModel
from fastapi import HTTPException
from app.tests.conftest import get_db_fixture


@pytest.fixture
async def member_service():
    return MemberService()


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_demote_member_from_admin_success(
    mock_get_member, mock_get_company, get_db_fixture, member_service
):
    member_service = await member_service
    user_id = 1
    member_id = 2
    company_id = 1

    mock_member = MemberModel(id=member_id, company_id=company_id, role="admin")
    mock_company = CompanyModel(id=company_id, owner_id=user_id, members=[mock_member])

    mock_get_company.return_value = mock_company
    mock_get_member.return_value = mock_member

    async for db_session in get_db_fixture:
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        result = await member_service.demote_member_from_admin(
            user_id=user_id, member_id=member_id, company_id=company_id, db=db_session
        )
        assert result.role == "member"
        mock_get_company.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_member.assert_called_once_with(id_=member_id, db=db_session)
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once_with(mock_member)


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_demote_member_from_admin_errors(
    mock_get_member, mock_get_company, get_db_fixture, member_service
):
    member_service = await member_service
    user_id = 1
    member_id = 2
    company_id = 1
    mock_get_company.return_value = None  # Company not found

    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await member_service.demote_member_from_admin(
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
            await member_service.demote_member_from_admin(
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
            await member_service.demote_member_from_admin(
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
    mock_get_member, mock_get_company, get_db_fixture, member_service
):
    member_service = await member_service
    user_id = 1
    member_id = 2
    company_id = 1
    mock_company = CompanyModel(id=company_id, owner_id=user_id)
    mock_member = MemberModel(id=member_id, company_id=company_id, role="admin")
    mock_get_company.return_value = mock_company
    mock_get_member.return_value = mock_member
    mock_company.members = [mock_member]

    async for db_session in get_db_fixture:
        result = await member_service.promote_member_to_admin(
            user_id=user_id, member_id=member_id, company_id=company_id, db=db_session
        )
        assert result.role == "admin"
        mock_get_company.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_member.assert_called_once_with(id_=member_id, db=db_session)


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_promote_member_to_admin_errors(
    mock_get_member, mock_get_company, get_db_fixture, member_service
):
    member_service = await member_service
    user_id = 1
    member_id = 2
    company_id = 1
    mock_get_company.return_value = None
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await member_service.promote_member_to_admin(
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
            await member_service.promote_member_to_admin(
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
            await member_service.promote_member_to_admin(
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
            await member_service.promote_member_to_admin(
                user_id=user_id,
                member_id=member_id,
                company_id=company_id,
                db=db_session,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Member not found in this company"


@pytest.mark.asyncio
@patch("app.services.member_service.member_crud")
@patch("app.services.member_service.company_crud")
async def test_fire_user_success(
    mock_company_crud, mock_member_crud, member_service, get_db_fixture
):
    member_service = await member_service
    mock_member = MemberModel(id=2, role="member", company_id=1)
    mock_company = CompanyModel(id=1, owner_id=1)

    mock_member_crud.get_one = AsyncMock(return_value=mock_member)
    mock_company_crud.get_one = AsyncMock(return_value=mock_company)
    mock_member_crud.delete = AsyncMock()

    async for db_session in get_db_fixture:
        result = await member_service.fire_user(id_=2, user_id=1, db=db_session)
        assert result == mock_member
        mock_member_crud.get_one.assert_called_once_with(id_=2, db=db_session)
        mock_company_crud.get_one.assert_called_once_with(
            id_=mock_member.company_id, db=db_session
        )
        mock_member_crud.delete.assert_called_once_with(id_=2, db=db_session)


@pytest.mark.asyncio
@patch("app.services.member_service.member_crud")
@patch("app.services.member_service.company_crud")
async def test_fire_user_errors(
    mock_company_crud, mock_member_crud, member_service, get_db_fixture
):
    member_service = await member_service
    async for db_session in get_db_fixture:
        mock_member_crud.get_one = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await member_service.fire_user(id_=1, user_id=1, db=db_session)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "There is no such a user"

        mock_member_crud.get_one = AsyncMock(
            return_value=MemberModel(id=1, company_id=1)
        )
        mock_company_crud.get_one = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await member_service.fire_user(id_=1, user_id=1, db=db_session)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Such a company was not found"

        mock_company_crud.get_one = AsyncMock(
            return_value=CompanyModel(id=1, owner_id=2)
        )
        with pytest.raises(HTTPException) as exc_info:
            await member_service.fire_user(id_=1, user_id=1, db=db_session)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You are not the owner of the company"


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_one", new_callable=AsyncMock)
@patch("app.CRUD.member_crud.member_crud.delete", new_callable=AsyncMock)
async def test_user_resign(mock_delete, mock_get_one, member_service):
    member_service = await member_service
    mock_get_one.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await member_service.user_resign(db=AsyncMock(), user_id=1)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You are not a member in any company"

    mock_get_one.return_value = MemberModel(id=1, company_id=1, role="member")
    mock_delete.return_value = None
    member = await member_service.user_resign(db=AsyncMock(), user_id=1)
    assert member.id == 1
    assert member.company_id == 1


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one", new_callable=AsyncMock)
@patch(
    "app.CRUD.member_crud.member_crud.get_all_by_filter_pagination",
    new_callable=AsyncMock,
)
async def test_get_users_in_company(
    mock_get_all_by_filter_pagination, mock_get_one, member_service
):
    member_service = await member_service
    mock_get_one.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await member_service.get_users_in_company(
            db=AsyncMock(), user_id=1, company_id=1, limit=10, offset=0
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Company not found"

    mock_get_one.return_value = CompanyModel(id=1, owner_id=2)
    with pytest.raises(HTTPException) as exc_info:
        await member_service.get_users_in_company(
            db=AsyncMock(), user_id=1, company_id=1, limit=10, offset=0
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You do not own company"

    mock_get_one.return_value = CompanyModel(id=1, owner_id=1)
    mock_get_all_by_filter_pagination.return_value = [
        MemberModel(id=1, company_id=1, role="member")
    ]
    members = await member_service.get_users_in_company(
        db=AsyncMock(), user_id=1, company_id=1, limit=10, offset=0
    )
    assert len(members) == 1
    assert members[0].id == 1
    assert members[0].company_id == 1
