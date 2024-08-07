from app.db.models.request_model import RequestModel
from app.repositories.crud_repository import CrudRepository


class RequestCrud(CrudRepository):
    pass


request_crud = RequestCrud(RequestModel)
