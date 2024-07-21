from app.repositories.crud_repository import CrudRepository
from app.db.models.models import QuestionModel


class QuestionCrud(CrudRepository):
    pass


question_crud = QuestionCrud(QuestionModel)
