from unittest.mock import MagicMock, AsyncMock
import pytest
from app.CRUD.company_crud import CompanyCrud
from app.db.models.company_model import CompanyModel


@pytest.fixture
async def company_crud():
    return CompanyCrud(CompanyModel)


@pytest.mark.asyncio
async def test_get_all_visible_success(get_db_fixture, company_crud):
    company_crud = await company_crud
    mock_visible_companies = [
        CompanyModel(id=1, name="Visible Company 1", visible=True),
        CompanyModel(id=2, name="Visible Company 2", visible=True),
    ]

    async for db_session in get_db_fixture:
        db_session.scalars.return_value.all = MagicMock(
            return_value=mock_visible_companies
        )
        result = await company_crud.get_all_visible(db=db_session)
        assert len(result) == 2
        assert result[0].name == "Visible Company 1"
        assert result[1].name == "Visible Company 2"
        assert result[0].visible is True
        assert result[1].visible is True
        db_session.scalars.assert_called_once()


@pytest.mark.asyncio
async def test_get_one_visible_success(get_db_fixture, company_crud):
    mock_company = CompanyModel(id=1, name="Visible Company", visible=True)
    company_crud = await company_crud
    async for db_session in get_db_fixture:
        db_session.scalar = AsyncMock(return_value=mock_company)
        result = await company_crud.get_one_visible(id_=1, db=db_session)
        assert result is not None
        assert result.id == 1
        assert result.name == "Visible Company"
        assert result.visible is True
        db_session.scalar.assert_called_once()
