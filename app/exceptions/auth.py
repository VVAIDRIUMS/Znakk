from app.exceptions.base import MyAppError, MyAppHTTPError


class UserAlreadyExistsError(MyAppError):
    detail = "Пользователь с таким email уже существует"


class InvalidJWTTokenError(MyAppError):
    detail = "Неверный токен"


class JWTTokenExpiredError(MyAppError):
    detail = "Токен истек, необходимо снова авторизоваться"


class InvalidPasswordError(MyAppError):
    detail = "Неверный пароль"


class UserNotFoundError(MyAppError):
    detail = "Пользователя не существует"


class InvalidTokenHTTPError(MyAppHTTPError):
    status_code = 401
    detail = "Неверный токен доступа"


class JWTTokenExpiredHTTPError(MyAppHTTPError):
    status_code = 401
    detail = "Токен истек, необходимо снова авторизоваться"


class NoAccessTokenHTTPError(MyAppHTTPError):
    detail = "Вы не предоставили токен доступа"
    status_code = 401


class UserAlreadyExistsHTTPError(MyAppHTTPError):
    status_code = 409
    detail = "Пользователь с таким email уже существует"


class UserNotFoundHTTPError(MyAppHTTPError):
    status_code = 401
    detail = "Пользователя не существует"


class InvalidPasswordHTTPError(MyAppHTTPError):
    status_code = 401
    detail = "Неверный пароль"
