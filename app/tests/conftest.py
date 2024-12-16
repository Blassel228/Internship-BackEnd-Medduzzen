from unittest.mock import AsyncMock
import pytest


@pytest.fixture
async def get_db_fixture():
    async with AsyncMock() as mock_db:
        yield mock_db
