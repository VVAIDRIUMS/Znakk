class UserNotFoundException(Exception):
    def __init__(self, identifier, by_email: bool = False):
        if by_email:
            message = f"User with email '{identifier}' not found"
        else:
            message = f"User with id {identifier} not found"
        super().__init__(message)
        self.identifier = identifier


class UserAlreadyExistsException(Exception):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")
        self.email = email


class InvalidCredentialsException(Exception):
    def __init__(self):
        super().__init__("Incorrect email or password")


class InvalidPasswordException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedException(Exception):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message)