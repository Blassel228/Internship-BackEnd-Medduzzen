from app.db.models.question_model import QuestionModel
from app.repositories.crud_repository import CrudRepository


class QuestionCrud(CrudRepository):
    pass


question_crud = QuestionCrud(QuestionModel)
