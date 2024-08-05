from app.db.models.models import InvitationModel
from app.repositories.crud_repository import CrudRepository


class InvitationCrud(CrudRepository):
    pass


invitation_crud = InvitationCrud(InvitationModel)
