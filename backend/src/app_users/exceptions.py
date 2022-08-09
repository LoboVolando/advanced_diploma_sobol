class AuthorBaseException(BaseException):
    """базовое исключение для сервиса авторов"""
    ...


class AuthorNotExists(AuthorBaseException):
    """Автор не существует"""
    ...


class PasswordIncorrect(AuthorBaseException):
    """пароль неправильный"""
    ...
