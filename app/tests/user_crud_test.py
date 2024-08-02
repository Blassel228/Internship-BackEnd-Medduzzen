import pytest
from app.db.models.models import UserModel
from app.CRUD.user_crud import UserCrud
from app.schemas.schemas import UserCreateSchema, UserUpdateInSchema
from app.tests.conftest import get_db_fixture
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.utils.deps import pwd_context


@pytest.fixture
def user_crud():
    return UserCrud(UserModel)


@pytest.mark.asyncio
async def test_get_all(user_crud, get_db_fixture):
    mock_users = [
        UserModel(id=1, username="user1", email="user1@example.com"),
        UserModel(id=2, username="user2", email="user2@example.com"),
    ]

    async for db_session in get_db_fixture:
        mock_res = MagicMock()
        db_session.scalars.return_value = mock_res
        mock_res.all.return_value = mock_users
        users = await user_crud.get_all(db=db_session)
        db_session.scalars.assert_called_once()
        assert len(users) == 2
        assert users[0].username == "user1"
        assert users[1].username == "user2"


@pytest.mark.asyncio
async def test_get_one_success(user_crud, get_db_fixture):
    mock_user = UserModel(id=1, username="user1", email="user1@example.com")
    async for db_session in get_db_fixture:
        db_session.scalar.return_value = mock_user
        user = await user_crud.get_one(id_=1, db=db_session)
        db_session.scalar.assert_called_once()
        assert user.id == 1
        assert user.username == "user1"


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.UserCrud.get_one", new_callable=AsyncMock)
async def test_delete_user_success(mock_get_one, user_crud, get_db_fixture):
    user_id = 1
    mock_user = UserModel(
        id=user_id,
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
    )
    mock_get_one.return_value = mock_user
    async for db_session in get_db_fixture:
        db_session.execute = AsyncMock()
        db_session.commit = AsyncMock()
        result = await user_crud.delete(id_=user_id, db=db_session)
        assert result == mock_user
        db_session.execute.assert_called_once()
        db_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.UserCrud.get_one", new_callable=AsyncMock)
async def test_add_user_success(mock_get_one, user_crud, get_db_fixture):
    user_data = {
        "id": 1,
        "username": "test_user",
        "password": "test_password",
        "email": "test@example.com",
    }
    user_create_schema = UserCreateSchema(**user_data)
    async for db_session in get_db_fixture:
        db_session.execute = AsyncMock()
        db_session.commit = AsyncMock()
        hashed_password = pwd_context.hash(user_data.pop("password"))
        mock_get_one.return_value = UserModel(
            **user_data, hashed_password=hashed_password
        )
        result = await user_crud.add(data=user_create_schema, db=db_session)
        assert result.id == 1
        assert result.username == "test_user"
        assert result.hashed_password == hashed_password
        db_session.execute.assert_called_once()
        db_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.UserCrud.get_one", new_callable=AsyncMock)
async def test_add_user_failure(mock_get_one, user_crud, get_db_fixture):
    user_data = {
        "id": 1,
        "username": "test_user",
        "password": "test_password",
        "email": "test@example.com",
    }
    user_create_schema = UserCreateSchema(**user_data)
    mock_get_one.return_value = None

    async for db_session in get_db_fixture:
        db_session.execute = AsyncMock()
        db_session.commit = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await user_crud.add(data=user_create_schema, db=db_session)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Something went wrong when adding a user"


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.UserCrud.update", new_callable=AsyncMock)
async def test_user_update_success(mock_update, user_crud, get_db_fixture):
    user_data = {
        "id": 2,
        "username": "updated_user",
        "password": "new_password",
        "email": "updated@example.com",
    }
    user_update_schema = UserUpdateInSchema(**user_data)
    hashed_password = pwd_context.hash(user_data.pop("password"))
    mock_user = UserModel(**user_data, hashed_password=hashed_password)
    async for db_session in get_db_fixture:
        mock_update.return_value = mock_user
        result = await user_crud.update(id_=1, data=user_update_schema, db=db_session)
        assert result.id == 2
        assert result.username == "updated_user"
        assert result.email == "updated@example.com"
        assert result.hashed_password == mock_user.hashed_password
        mock_update.assert_called_once()


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.logger")
async def test_update_user_not_found(mock_logger, get_db_fixture, user_crud):
    user_id = 1

    mock_get_one = AsyncMock(return_value=None)
    user_crud.get_one = mock_get_one

    user_data = {
        "username": "updated_user",
        "password": "new_password",
        "email": "updated@example.com",
    }
    user_update_schema = UserUpdateInSchema(**user_data)

    async for db_session in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await user_crud.update(id_=user_id, data=user_update_schema, db=db_session)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User was not found"
        mock_logger.error.assert_not_called()


@pytest.mark.asyncio
@patch("app.CRUD.user_crud.logger")
async def test_update_user_database_error(mock_logger, get_db_fixture, user_crud):
    user_id = 1

    mock_user = UserModel(id=user_id, username="old_user", email="old@example.com")
    mock_get_one = AsyncMock(return_value=mock_user)
    user_crud.get_one = mock_get_one

    async def mock_execute_raise_exception(*args, **kwargs):
        raise Exception("Database error")

    db_session = AsyncMock()
    db_session.execute = AsyncMock(side_effect=mock_execute_raise_exception)

    user_data = {
        "username": "updated_user",
        "password": "new_password",
        "email": "updated@example.com",
    }
    user_update_schema = UserUpdateInSchema(**user_data)

    async for _ in get_db_fixture:
        with pytest.raises(HTTPException) as exc_info:
            await user_crud.update(id_=user_id, data=user_update_schema, db=db_session)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Something went wrong while updating the user"
        mock_logger.error.assert_called_once_with("Error updating user: Database error")
