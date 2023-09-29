from exceptions import BaseCustomException
from rapidpro.constants import ExceptionMessages


class ObjectDoesNotUpdatedExeption(BaseCustomException):

    def __init__(self, dababase_object) -> None:
        self.database_object_name = dababase_object.__name__
        self.message = ExceptionMessages.OBJECT_DOES_NOT_UPDATED.format(
            self.dababase_object_name
        )
        super().__init__(self.message)
