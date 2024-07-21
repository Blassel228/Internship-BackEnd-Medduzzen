from app.repositories.crud_repository import CrudRepository
from app.db.models.models import OptionModel


class OptionCrud(CrudRepository):
    pass


option_crud = OptionCrud(OptionModel)
