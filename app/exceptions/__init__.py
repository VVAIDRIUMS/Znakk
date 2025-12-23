# app/exceptions/__init__.py
from .favorites import FavoriteNotFoundException, FavoriteAlreadyExistsException
from .likes import LikeNotFoundException, LikeAlreadyExistsException
from .profiles import (
    ProfileNotFoundException, 
    ProfileAlreadyExistsException, 
    InvalidProfileDataException
)
from .roles import (
    RoleNotFoundException,
    RoleAlreadyExistsException,
    RoleHasUsersException
)
from .user_filters import (
    UserFilterNotFoundException,
    UserFilterAlreadyExistsException,
    InvalidFilterDataException
)
from .users import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidPasswordException,
    UnauthorizedException
)

__all__ = [
    "FavoriteNotFoundException",
    "FavoriteAlreadyExistsException",
    "LikeNotFoundException",
    "LikeAlreadyExistsException",
    "ProfileNotFoundException",
    "ProfileAlreadyExistsException",
    "InvalidProfileDataException",
    "RoleNotFoundException",
    "RoleAlreadyExistsException",
    "RoleHasUsersException",
    "UserFilterNotFoundException",
    "UserFilterAlreadyExistsException",
    "InvalidFilterDataException",
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "InvalidCredentialsException",
    "InvalidPasswordException",
    "UnauthorizedException",
]