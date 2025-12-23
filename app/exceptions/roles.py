class RoleNotFoundException(Exception):
    def __init__(self, identifier, by_name: bool = False):
        if by_name:
            message = f"Role with name '{identifier}' not found"
        else:
            message = f"Role with id {identifier} not found"
        super().__init__(message)
        self.identifier = identifier


class RoleAlreadyExistsException(Exception):
    def __init__(self, name: str):
        super().__init__(f"Role with name '{name}' already exists")
        self.name = name


class RoleHasUsersException(Exception):
    def __init__(self, role_id: int, user_count: int):
        super().__init__(
            f"Cannot delete role with id {role_id} because it has {user_count} associated users. "
            f"Remove users from this role first."
        )
        self.role_id = role_id
        self.user_count = user_count