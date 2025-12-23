class UserFilterNotFoundException(Exception):
    def __init__(self, identifier, by_user_id: bool = False):
        if by_user_id:
            message = f"User filter for user_id {identifier} not found"
        else:
            message = f"User filter with id {identifier} not found"
        super().__init__(message)
        self.identifier = identifier


class UserFilterAlreadyExistsException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"User filter for user_id {user_id} already exists")
        self.user_id = user_id


class InvalidFilterDataException(Exception):
    def __init__(self, message: str):
        super().__init__(message)