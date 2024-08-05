from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.db.models.models import InvitationModel, CompanyModel, MemberModel
from app.schemas.schemas import InvitationCreateSchema, MemberCreateSchema
from app.services.invitation_service import InvitationService
from app.tests.conftest import get_db_fixture


@pytest.fixture()
async def invitation_service():
    return InvitationService()


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.get_all_by_filter")
async def test_owner_get_all_invitations_success(
    mock_get_all_by_filter, mock_get_one, invitation_service, get_db_fixture
):
    invitation_service = await invitation_service
    user_id = 1
    company_id = 1

    mock_company = CompanyModel(id=company_id, owner_id=user_id)
    mock_get_one.return_value = mock_company
    mock_invitations = [
        InvitationModel(id=1, company_id=company_id),
        InvitationModel(id=2, company_id=company_id),
    ]
    mock_get_all_by_filter.return_value = mock_invitations

    async for db_session in get_db_fixture:
        result = await invitation_service.owner_get_all_invitations(
            user_id=user_id, company_id=company_id, db=db_session
        )
        assert result == mock_invitations
        mock_get_one.assert_called_once_with(id_=company_id, db=db_session)
        mock_get_all_by_filter.assert_called_once_with(
            filters={"company_id": company_id}, db=db_session
        )


@pytest.mark.asyncio
@patch("app.CRUD.company_crud.company_crud.get_one")
async def test_owner_get_all_invitations_errors(
    mock_get_one, invitation_service, get_db_fixture
):
    invitation_service = await invitation_service
    user_id = 1
    company_id = 1

    # Test company not found
    mock_get_one.return_value = None
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.owner_get_all_invitations(
                user_id=user_id, company_id=company_id, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Such a company does not exist"

    mock_get_one.return_value = CompanyModel(id=company_id, owner_id=2)
    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.owner_get_all_invitations(
                user_id=user_id, company_id=company_id, db=db_session
            )
        assert exc_info.value.status_code == 403
        assert (
            exc_info.value.detail == "You do not own the company to get the invitations"
        )


@pytest.mark.asyncio
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.add")
async def test_send_invitation_success(
    mock_add,
    mock_get_member,
    mock_get_company,
    mock_get_invitation,
    invitation_service,
    get_db_fixture,
):
    invitation_service = await invitation_service
    user_id = 1
    data = InvitationCreateSchema(
        id=1, recipient_id=2, company_id=1, invitation_text="Test"
    )

    mock_get_invitation.return_value = None
    mock_get_company.return_value = CompanyModel(id=1, owner_id=1)
    mock_get_member.return_value = None
    mock_add.return_value = InvitationModel(
        id=1, recipient_id=2, company_id=1, invitation_text="Test"
    )

    async for db_session in get_db_fixture:
        result = await invitation_service.send_invitation(
            user_id=user_id, data=data, db=db_session
        )
        assert result.id == 1
        assert result.recipient_id == 2
        assert result.company_id == 1
        mock_get_invitation.assert_called_once_with(id_=data.id, db=db_session)
        mock_get_company.assert_called_once_with(id_=data.company_id, db=db_session)
        mock_get_member.assert_called_once_with(id_=data.recipient_id, db=db_session)
        mock_add.assert_called_once_with(data=data, db=db_session)


@pytest.mark.asyncio
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.get_one")
async def test_send_invitation_errors(
    mock_get_member,
    mock_get_company,
    mock_get_invitation,
    invitation_service,
    get_db_fixture,
):
    invitation_service = await invitation_service
    user_id = 1
    data = InvitationCreateSchema(
        id=1, recipient_id=2, company_id=1, invitation_text="Test"
    )

    async for db_session in get_db_fixture:
        # Test invitation already exists
        mock_get_invitation.return_value = InvitationModel(
            id=1, recipient_id=2, company_id=1, invitation_text="Test"
        )
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.send_invitation(
                user_id=user_id, data=data, db=db_session
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Such an invitation already exists"

        # Reset mocks
        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_get_member.reset_mock()

        # Test cannot send invitation to itself
        mock_get_invitation.return_value = None
        data.recipient_id = user_id
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.send_invitation(
                user_id=user_id, data=data, db=db_session
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Cannot send invitation to itself"

        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_get_member.reset_mock()

        data.recipient_id = 2
        mock_get_company.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.send_invitation(
                user_id=user_id, data=data, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "There is no such a company"

        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_get_member.reset_mock()

        mock_get_company.return_value = CompanyModel(id=1, owner_id=2)
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.send_invitation(
                user_id=user_id, data=data, db=db_session
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You do not own the company to send invitations"

        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_get_member.reset_mock()

        mock_get_company.return_value = CompanyModel(id=1, owner_id=1)
        mock_get_member.return_value = MemberModel(id=2, company_id=1)
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.send_invitation(
                user_id=user_id, data=data, db=db_session
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "The user is in your company already"


@pytest.mark.asyncio
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.delete")
async def test_delete_invitation_by_owner_success(
    mock_delete_invitation,
    mock_get_company,
    mock_get_invitation,
    invitation_service,
    get_db_fixture,
):
    invitation_service = await invitation_service
    user_id = 1
    invitation_id = 1

    async for db_session in get_db_fixture:
        mock_get_invitation.return_value = InvitationModel(
            id=invitation_id, company_id=1
        )
        mock_get_company.return_value = CompanyModel(id=1, owner_id=user_id)
        mock_delete_invitation.return_value = None

        result = await invitation_service.delete_invitation_by_owner(
            id_=invitation_id, user_id=user_id, db=db_session
        )
        assert result == mock_get_invitation.return_value
        mock_delete_invitation.assert_awaited_once_with(
            id_=invitation_id, db=db_session
        )


@pytest.mark.asyncio
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.delete")
async def test_delete_invitation_by_owner_errors(
    mock_delete_invitation,
    mock_get_company,
    mock_get_invitation,
    invitation_service,
    get_db_fixture,
):
    invitation_service = await invitation_service
    user_id = 1
    invitation_id = 1

    async for db_session in get_db_fixture:
        mock_get_invitation.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.delete_invitation_by_owner(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Such an invitation does not exist"

        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_delete_invitation.reset_mock()

        mock_get_invitation.return_value = InvitationModel(
            id=invitation_id, company_id=1
        )
        mock_get_company.return_value = CompanyModel(id=1, owner_id=2)
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.delete_invitation_by_owner(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 403
        assert (
            exc_info.value.detail
            == "You do not possess the company to delete invitations"
        )


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.add")
@patch("app.CRUD.invitation_crud.invitation_crud.delete")
async def test_accept_invitation_success(
    mock_delete_invitation,
    mock_add_member,
    mock_get_company,
    mock_get_invitation,
    mock_get_member,
    invitation_service,
    get_db_fixture,
):
    invitation_service = await invitation_service
    user_id = 1
    invitation_id = 1

    async for db_session in get_db_fixture:
        mock_get_member.return_value = None
        mock_get_invitation.return_value = InvitationModel(
            id=invitation_id, recipient_id=user_id, company_id=1
        )
        mock_get_company.return_value = CompanyModel(id=1, owner_id=2)
        mock_add_member.return_value = MemberModel(id=user_id, company_id=1)

        result = await invitation_service.accept_invitation(
            id_=invitation_id, user_id=user_id, db=db_session
        )

        assert result == mock_add_member.return_value
        mock_add_member.assert_awaited_once_with(
            db=db_session, data=MemberCreateSchema(company_id=1, id=user_id)
        )
        mock_delete_invitation.assert_awaited_once_with(
            id_=invitation_id, db=db_session
        )


@pytest.mark.asyncio
@patch("app.CRUD.member_crud.member_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.company_crud.company_crud.get_one")
@patch("app.CRUD.member_crud.member_crud.add")
@patch("app.CRUD.invitation_crud.invitation_crud.delete")
async def test_accept_invitation_errors(
    mock_delete_invitation,
    mock_add_member,
    mock_get_company,
    mock_get_invitation,
    mock_get_member,
    invitation_service,
    get_db_fixture,
):
    invitation_service = await invitation_service
    user_id = 1
    invitation_id = 1

    async for db_session in get_db_fixture:
        mock_get_member.return_value = MemberModel(id=user_id, company_id=1)
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.accept_invitation(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "You are in a company already"

        mock_get_member.reset_mock()
        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_add_member.reset_mock()
        mock_delete_invitation.reset_mock()

        mock_get_member.return_value = None
        mock_get_invitation.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.accept_invitation(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "The invitation with such an id does not exist"

        mock_get_member.reset_mock()
        mock_get_invitation.reset_mock()
        mock_get_company.reset_mock()
        mock_add_member.reset_mock()
        mock_delete_invitation.reset_mock()

        mock_get_member.return_value = None
        mock_get_invitation.return_value = InvitationModel(
            id=invitation_id, recipient_id=2, company_id=1
        )
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.accept_invitation(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "You do not have such an invitation to accept"


@pytest.mark.asyncio
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.delete")
async def test_reject_invitation_success(
    mock_delete_invitation, mock_get_invitation, invitation_service, get_db_fixture
):
    invitation_service = await invitation_service
    user_id = 1
    invitation_id = 1

    async for db_session in get_db_fixture:
        mock_get_invitation.return_value = InvitationModel(
            id=invitation_id, recipient_id=user_id, company_id=1
        )
        mock_delete_invitation.return_value = None

        result = await invitation_service.reject_invitation(
            id_=invitation_id, user_id=user_id, db=db_session
        )

        assert result.id == invitation_id
        assert result.recipient_id == user_id
        mock_get_invitation.assert_awaited_once_with(id_=invitation_id, db=db_session)
        mock_delete_invitation.assert_awaited_once_with(
            id_=invitation_id, db=db_session
        )


@pytest.mark.asyncio
@patch("app.CRUD.invitation_crud.invitation_crud.get_one")
@patch("app.CRUD.invitation_crud.invitation_crud.delete")
async def test_reject_invitation_errors(
    mock_delete_invitation, mock_get_invitation, invitation_service, get_db_fixture
):
    invitation_service = await invitation_service
    user_id = 1
    invitation_id = 1

    async for db_session in get_db_fixture:
        mock_get_invitation.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.reject_invitation(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "The invitation with such an id does not exist"

        mock_get_invitation.reset_mock()
        mock_delete_invitation.reset_mock()

        mock_get_invitation.return_value = InvitationModel(
            id=invitation_id, recipient_id=2, company_id=1
        )
        with pytest.raises(HTTPException) as exc_info:
            await invitation_service.reject_invitation(
                id_=invitation_id, user_id=user_id, db=db_session
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "You do not have such a invitation to delete"
