from app.core.exc.base import ServerErrorException, UnauthorizedException


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self) -> None:
        self.message = "Invalid credentials provided"
        super().__init__(self.message)


class UserNotAuthenticatedException(UnauthorizedException):
    def __init__(self) -> None:
        self.message = "User not authenticated"
        super().__init__(self.message)


class AuthServiceException(ServerErrorException):
    def __init__(self) -> None:
        self.message = "Error communicating with authentication service"
        super().__init__(self.message)
