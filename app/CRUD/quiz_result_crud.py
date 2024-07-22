from app.db.models.models import QuizResultModel
from app.repositories.crud_repository import CrudRepository


class QuizResultCrud(CrudRepository):
    pass


quiz_result_crud = QuizResultCrud(QuizResultModel)
