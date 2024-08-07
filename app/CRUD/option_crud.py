from app.db.models.option_model import OptionModel
from app.repositories.crud_repository import CrudRepository


class OptionCrud(CrudRepository):
    pass


option_crud = OptionCrud(OptionModel)
