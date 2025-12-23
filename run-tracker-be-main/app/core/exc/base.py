from typing import Any


class ObjectNotFoundException(Exception):
    def __init__(self, id_: Any, entity_name: str) -> None:
        msg = (
            f"{entity_name} with given identifier - {id_} not found"
            if id_
            else f"{entity_name} not found"
        )
        super().__init__(msg)


class BadRequestException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ObjectAlreadyExistsException(Exception):
    def __init__(self, id_: Any, entity_name: str) -> None:
        msg = (
            f"{entity_name} with given identifier - {id_} already exists"
            if id_
            else f"{entity_name} already exists"
        )
        super().__init__(msg)


class ServerErrorException(Exception):
    def __init__(self, message: str) -> None:
        self.message = f"Server error. {message}"
        super().__init__(self.message)


class UnauthorizedException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ForbiddenException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
