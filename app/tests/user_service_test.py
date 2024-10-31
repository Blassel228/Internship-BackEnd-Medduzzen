from unittest.mock import patch
from app.autho.autho import pwd_context
from app.schemas.schemas import UserUpdateInSchema
from app.services.user_service import UserService
from fastapi import HTTPException
import pytest
from app.tests.conftest import get_db_fixture


@pytest.fixture
async def user_service():
    return UserService()


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.user_crud.update")
async def test_self_update_success(mock_update, user_service, get_db_fixture):
    user_id = 1
    new_password = "new_password"
    update_data = UserUpdateInSchema(
        id=user_id,
        username="updated_username",
        password=new_password,
        email="new_email@example.com",
    )
    mock_user = {
        "id": user_id,
        "username": "updated_username",
        "mail": "new_email@example.com",
    }
    mock_update.return_value = mock_user
    service = await user_service
    result = await service.self_update(user_id, get_db_fixture, update_data)
    assert result == mock_user
    mock_update.assert_called_once()
    called_args, called_kwargs = mock_update.call_args
    assert called_kwargs["id_"] == user_id
    assert called_kwargs["db"] == get_db_fixture
    called_data = called_kwargs["data"].model_dump()
    assert called_data["username"] == "updated_username"
    assert "hashed_password" in called_data
    assert pwd_context.verify(new_password, called_data["hashed_password"])


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.user_crud.update")
async def test_self_update_error(mock_update, user_service, get_db_fixture):
    user_id = 1
    invalid_data = "invalid_json"
    mock_update.return_value = None
    service = await user_service
    with pytest.raises(HTTPException) as exc_info:
        await service.self_update(user_id, get_db_fixture, invalid_data)
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Request body is not valid JSON."
    mock_update.assert_not_called()
