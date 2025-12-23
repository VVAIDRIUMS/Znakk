class ProfileNotFoundException(Exception):
    def __init__(self, identifier, by_user_id: bool = False, by_username: bool = False):
        if by_user_id:
            message = f"Profile with user_id {identifier} not found"
        elif by_username:
            message = f"Profile with username {identifier} not found"
        else:
            message = f"Profile with id {identifier} not found"
        super().__init__(message)
        self.identifier = identifier


class ProfileAlreadyExistsException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidProfileDataException(Exception):
    def __init__(self, message: str):
        super().__init__(message)