

from rapidpro.constants import DEFAULT_USER_ID
from rapidpro.database.users import RapidProUser
from rapidpro.exceptions.object_does_not_exist_exception import ObjectDoesNotExistException
from rapidpro.services.base_service import BaseService


class UserService(BaseService):

    def __init__(self, db_connection=None) -> None:
        super().__init__(db_connection=db_connection)

        # model table entities
        self.user = RapidProUser

    def get_default_user(self):

        default_user = self.db_connection.session.query(self.user).filter_by(
            id=DEFAULT_USER_ID
        ).first()

        if default_user:
            return default_user
        else:
            raise ObjectDoesNotExistException(dababase_object=self.user)
