from exceptions import BaseCustomException
from rapidpro.constants import ExceptionMessages


class FlowNameLongerException(BaseCustomException):

    def __init__(self, max_lenght) -> None:
        self.message = ExceptionMessages.FLOW_NAME_LONGER.format(max_lenght)
        super().__init__(self.message)


class FlowNameStartsOrEndWithWhitespaceException(BaseCustomException):

    def __init__(self) -> None:
        self.message = ExceptionMessages.FLOW_NAME_STARTS_OR_END_WITH_WHITESPACE
        super().__init__(self.message)


class FlowNameInvalidCharacterException(BaseCustomException):

    def __init__(self, invalid_char) -> None:
        self.message = ExceptionMessages.FLOW_INVALID_CHARACTERS.format(invalid_char)
        super().__init__(self.message)


class FlowNameContainsNullCharacterException(BaseCustomException):

    def __init__(self) -> None:
        self.message = ExceptionMessages.FLOW_NAME_CONTAINS_NULL_CHARACTER
        super().__init__(self.message)
