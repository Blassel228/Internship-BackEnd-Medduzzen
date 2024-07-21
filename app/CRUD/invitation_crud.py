from app.repositories.crud_repository import CrudRepository
from app.db.models.models import InvitationModel


class InvitationCrud(CrudRepository):
    pass


invitation_crud = InvitationCrud(InvitationModel)
