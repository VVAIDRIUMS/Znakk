from fastapi import HTTPException


class MyAppError(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class MyAppHTTPError(HTTPException):
    status_code = 500
    detail = "Неожиданная ошибка"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectNotFoundError(MyAppError):
    detail = "Объект не найден"


class ObjectAlreadyExistsError(MyAppError):
    detail = "Похожий объект уже существует"


class InvalidDateRangeError(MyAppError):
    detail = "Дата заезда не может быть позже даты выезда"
