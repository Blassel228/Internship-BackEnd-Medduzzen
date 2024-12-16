from app.db.models.quiz_result_model import QuizResultModel
from app.repositories.crud_repository import CrudRepository


class QuizResultCrud(CrudRepository):
    pass


quiz_result_crud = QuizResultCrud(QuizResultModel)
