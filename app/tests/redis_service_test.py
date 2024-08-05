import json
from unittest.mock import patch, MagicMock, AsyncMock, call
import pytest
from fastapi import HTTPException
from app.db.models.models import MemberModel, CompanyModel
from app.services.redis_service import RedisService


@pytest.fixture
async def redis_service():
    return RedisService()


@pytest.fixture
def test_data():
    return {
        "id_": 1,
        "quiz_id": 123,
        "user_id": 456,
        "company_id": 789,
        "score": 95,
        "company_name": "Valid Company",
    }


@pytest.mark.asyncio
@patch("app.services.redis_service.redis_connect")
async def test_cache_quiz_result_success(mock_redis_connect, test_data):
    mock_redis = AsyncMock()
    mock_redis_connect.return_value = mock_redis
    redis_service = RedisService()
    await redis_service.cache_quiz_result(test_data)
    expected_key = f"quiz_result:{test_data['quiz_id']}:{test_data['user_id']}:{test_data['company_id']}"
    expected_value = json.dumps(test_data)

    mock_redis.set.assert_called_once_with(expected_key, expected_value, ex=172800)


@pytest.mark.asyncio
@patch("app.services.redis_service.redis_connect")
async def test_cache_quiz_result_redis_error(mock_redis_connect, test_data):
    mock_redis = MagicMock()
    mock_redis_connect.return_value = mock_redis
    mock_redis.set.side_effect = Exception("Redis error")
    redis_service = RedisService()
    with pytest.raises(Exception, match="Redis error"):
        await redis_service.cache_quiz_result(test_data)


@pytest.mark.asyncio
@patch("app.services.redis_service.redis_connect", autospec=True)
@patch("app.services.redis_service.member_crud.get_one")
@patch("app.services.redis_service.company_crud.get_one_by_filter")
async def test_get_from_cache_success(
    mock_get_company, mock_get_member, mock_redis_connect, redis_service, get_db_fixture
):
    mock_redis = AsyncMock()
    mock_redis_connect.return_value = mock_redis
    mock_redis.keys.return_value = ["key"]
    mock_redis.mget.return_value = [json.dumps({"data": "value"})]

    mock_get_member.return_value = MemberModel(id=1, role="admin", company_id=1)
    mock_get_company.return_value = CompanyModel(id=1, owner_id=1)

    redis_service = await redis_service

    async for session in get_db_fixture:
        result = await redis_service.get_from_cache("key", 1, session, "Valid Company")

        assert result == [{"data": "value"}]
        mock_redis.keys.assert_called_once_with("key")
        mock_redis.mget.assert_called_once_with(["key"])
        mock_get_member.assert_called_once_with(id_=1, db=session)
        mock_get_company.assert_called_once_with(
            filters={"name": "Valid Company"}, db=session
        )


@pytest.mark.asyncio
@patch("app.services.redis_service.redis_connect", autospec=True)
@patch("app.services.redis_service.member_crud.get_one")
@patch("app.services.redis_service.company_crud.get_one_by_filter")
async def test_get_from_cache_errors(
    mock_get_company, mock_get_member, mock_redis_connect, redis_service, get_db_fixture
):
    mock_redis = AsyncMock()
    mock_redis_connect.return_value = mock_redis

    redis_service = await redis_service

    async for session in get_db_fixture:
        # Test 1: Company not found
        mock_get_member.return_value = AsyncMock(id=1, role="admin", company_id=1)
        mock_get_company.return_value = None
        with pytest.raises(HTTPException, match="There is no such a company"):
            await redis_service.get_from_cache("key", 1, session, "Invalid Company")

        mock_get_company.return_value = AsyncMock(id=1, owner_id=1)
        mock_get_member.return_value = AsyncMock(id=2, role="member", company_id=2)
        with pytest.raises(HTTPException, match="You do not have such rights"):
            await redis_service.get_from_cache("key", 1, session, "Valid Company")

        # Test 3: Unauthorized access (not a member of the company)
        mock_get_member.return_value = AsyncMock(id=1, role="admin", company_id=2)
        with pytest.raises(HTTPException, match="You are not a member of the company"):
            await redis_service.get_from_cache("key", 1, session, "Valid Company")

        # Test 4: Cache not found
        mock_get_member.return_value = AsyncMock(id=1, role="admin", company_id=1)
        mock_get_company.return_value = AsyncMock(id=1, owner_id=1)
        mock_redis.mget.return_value = []
        with pytest.raises(HTTPException, match="Cache was not found"):
            await redis_service.get_from_cache("key", 1, session, "Valid Company")

        assert mock_get_member.call_count == 4
        assert mock_get_company.call_count == 4
        assert mock_get_member.call_args_list == [call(id_=1, db=session)] * 4
        assert mock_get_company.call_args_list == [
            call(filters={"name": "Invalid Company"}, db=session),
            call(filters={"name": "Valid Company"}, db=session),
            call(filters={"name": "Valid Company"}, db=session),
            call(filters={"name": "Valid Company"}, db=session),
        ]


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.get_from_cache")
async def test_admin_get_cache_for_user(
    mock_get_from_cache, redis_service, test_data, get_db_fixture
):
    redis_service = await redis_service

    id_ = 1
    quiz_id = test_data["quiz_id"]
    user_id = test_data["user_id"]
    company_name = "Valid Company"
    expected_key = f"quiz_result:{quiz_id}:{id_}:*"

    async for session in get_db_fixture:
        # Call the method under test
        await redis_service.admin_get_cache_for_user(
            id_=id_,
            quiz_id=quiz_id,
            user_id=user_id,
            db=session,
            company_name=company_name,
        )

        mock_get_from_cache.assert_called_once_with(
            key=expected_key, db=session, user_id=user_id, company_name=company_name
        )


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.get_from_cache")
async def test_get_cached_result(
    mock_get_from_cache, redis_service, test_data, get_db_fixture
):
    redis_service = await redis_service

    quiz_id = test_data["quiz_id"]
    user_id = test_data["user_id"]
    company_name = "Valid Company"
    expected_key = f"quiz_result:{quiz_id}:{user_id}:*"

    async for session in get_db_fixture:
        await redis_service.get_cached_result(
            quiz_id=quiz_id, user_id=user_id, db=session, company_name=company_name
        )

        mock_get_from_cache.assert_called_once_with(
            key=expected_key, db=session, user_id=user_id, company_name=company_name
        )


@pytest.mark.asyncio
@patch("app.services.redis_service.redis_connect")
async def test_user_get_its_result_success(
    mock_redis_connect, test_data, redis_service, get_db_fixture
):
    redis_service = await redis_service
    redis = mock_redis_connect.return_value
    key = f"quiz_result:*:{test_data['user_id']}:*"

    cache_data = [
        json.dumps(
            {
                "quiz_id": test_data["quiz_id"],
                "user_id": test_data["user_id"],
                "score": test_data["score"],
            }
        )
    ]
    redis.keys = AsyncMock(return_value=[key])
    redis.mget = AsyncMock(return_value=cache_data)

    result = await redis_service.user_get_its_result(user_id=test_data["user_id"])
    assert result == [json.loads(data) for data in cache_data]
    redis.keys.assert_awaited_once_with(key)
    redis.mget.assert_awaited_once_with([key])


@pytest.mark.asyncio
@patch("app.services.redis_service.company_crud.get_one_by_filter")
@patch("app.services.redis_service.RedisService.get_from_cache")
async def test_admin_get_all_cache_by_company_id_success(
    mock_get_from_cache,
    mock_get_company_by_filter,
    redis_service,
    test_data,
    get_db_fixture,
):
    redis_service = await redis_service

    mock_get_company_by_filter.return_value = AsyncMock(
        id=test_data["company_id"], name=test_data["company_name"]
    )

    expected_key = f"quiz_result:*:*:{test_data['company_id']}"

    cache_data = [
        json.dumps(
            {
                "quiz_id": test_data["quiz_id"],
                "user_id": test_data["user_id"],
                "score": test_data["score"],
            }
        )
    ]
    mock_get_from_cache.return_value = [json.loads(data) for data in cache_data]

    async for session in get_db_fixture:
        result = await redis_service.admin_get_all_cache_by_company_id(
            user_id=test_data["user_id"],
            company_name=test_data["company_name"],
            db=session,
        )

        assert result == [json.loads(data) for data in cache_data]
        mock_get_from_cache.assert_called_once_with(
            key=expected_key,
            db=session,
            user_id=test_data["user_id"],
            company_name=test_data["company_name"],
        )


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.get_from_cache")
async def test_admin_get_all_results_by_quiz_id_success(
    mock_get_from_cache, redis_service, test_data, get_db_fixture
):
    redis_service = await redis_service

    # Define expected key based on test_data
    expected_key = f"quiz_result:{test_data['quiz_id']}:*:*"

    # Mock the cache data
    cache_data = [
        json.dumps(
            {
                "quiz_id": test_data["quiz_id"],
                "user_id": test_data["user_id"],
                "score": test_data["score"],
            }
        )
    ]
    mock_get_from_cache.return_value = [json.loads(data) for data in cache_data]

    async for session in get_db_fixture:
        # Call the method under test
        result = await redis_service.admin_get_all_results_by_quiz_id(
            quiz_id=test_data["quiz_id"],
            user_id=test_data["user_id"],
            company_name=test_data["company_name"],
            db=session,
        )

        # Assertions
        assert result == [json.loads(data) for data in cache_data]
        mock_get_from_cache.assert_called_once_with(
            key=expected_key,
            db=session,
            user_id=test_data["user_id"],
            company_name=test_data["company_name"],
        )


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.admin_get_cache_for_user")
@patch("app.services.redis_service.csv.writer")
@patch("app.services.redis_service.open")
async def test_export_cached_results_for_one_user_to_csv(
    mock_open,
    mock_csv_writer,
    mock_admin_get_cache_for_user,
    redis_service,
    test_data,
    get_db_fixture,
):
    redis_service = await redis_service

    # Mock data
    cache_data = [
        {
            "quiz_id": test_data["quiz_id"],
            "user_id": test_data["user_id"],
            "score": test_data["score"],
        }
    ]
    mock_admin_get_cache_for_user.return_value = cache_data

    # Mock the file operation
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    # Mock CSV writer
    mock_writer = MagicMock()
    mock_csv_writer.return_value = mock_writer

    async for session in get_db_fixture:
        result = await redis_service.export_cached_results_for_one_user_to_csv(
            user_id=test_data["user_id"],
            id_=test_data["id_"],
            quiz_id=test_data["quiz_id"],
            company_name=test_data["company_name"],
            db=session,
        )

        assert result == cache_data

        mock_open.assert_called_once_with("cache.csv", "w", newline="")
        mock_writer.writerow.assert_any_call(["quiz_id", "user_id", "score"])
        mock_writer.writerow.assert_any_call(
            [test_data["quiz_id"], test_data["user_id"], test_data["score"]]
        )


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.admin_get_cache_for_user")
async def test_export_cached_results_for_one_user_to_csv_no_cache(
    mock_admin_get_cache_for_user, redis_service, test_data, get_db_fixture
):
    redis_service = await redis_service

    mock_admin_get_cache_for_user.return_value = None

    async for session in get_db_fixture:
        with pytest.raises(HTTPException, match="Cache was not found"):
            await redis_service.export_cached_results_for_one_user_to_csv(
                user_id=test_data["user_id"],
                id_=test_data["id_"],
                quiz_id=test_data["quiz_id"],
                company_name=test_data["company_name"],
                db=session,
            )


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.admin_get_all_results_by_quiz_id")
@patch("app.services.redis_service.open")
@patch("app.services.redis_service.csv.writer")
async def test_export_all_cached_results_to_csv(
    mock_csv_writer,
    mock_open,
    mock_admin_get_all_results_by_quiz_id,
    redis_service,
    test_data,
    get_db_fixture,
):
    redis_service = await redis_service

    cache_data = [
        {
            "quiz_id": test_data["quiz_id"],
            "user_id": test_data["user_id"],
            "score": test_data["score"],
        }
    ]

    mock_admin_get_all_results_by_quiz_id.return_value = cache_data

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_writer = MagicMock()
    mock_csv_writer.return_value = mock_writer

    async for session in get_db_fixture:
        result = await redis_service.export_all_cached_results_to_csv(
            user_id=test_data["user_id"],
            quiz_id=test_data["quiz_id"],
            company_name=test_data["company_name"],
            db=session,
        )
        assert result == cache_data
        mock_open.assert_called_once_with("cache.csv", "w", newline="")

        expected_header = ["quiz_id", "user_id", "score"]
        expected_row = [test_data["quiz_id"], test_data["user_id"], test_data["score"]]

        mock_writer.writerow.assert_any_call(expected_header)
        mock_writer.writerow.assert_any_call(expected_row)
        assert mock_writer.writerow.call_count == 2


@pytest.mark.asyncio
@patch("app.services.redis_service.RedisService.admin_get_all_results_by_quiz_id")
async def test_export_all_cached_results_to_csv_no_cache(
    mock_admin_get_all_results_by_quiz_id, redis_service, test_data, get_db_fixture
):
    redis_service = await redis_service
    mock_admin_get_all_results_by_quiz_id.return_value = None

    async for session in get_db_fixture:
        with pytest.raises(HTTPException, match="Cache was not found"):
            await redis_service.export_all_cached_results_to_csv(
                user_id=test_data["user_id"],
                quiz_id=test_data["quiz_id"],
                company_name=test_data["company_name"],
                db=session,
            )
