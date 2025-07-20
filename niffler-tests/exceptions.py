

class NifflerError(Exception):
    """Базовое исключение для всех ошибок"""
    pass


class DatabaseError(NifflerError):
    """Ошибки работы с базой данных"""

    def __init__(self, message: str, username: str = None, operation: str = None):
        self.username = username
        self.operation = operation
        super().__init__(f"DB ERROR [{operation}] for user '{username}': {message}")


class UIError(NifflerError):
    """Ошибки UI взаимодействий"""

    def __init__(self, message: str, page: str = None, action: str = None):
        self.page = page
        self.action = action
        super().__init__(f"UI ERROR [{action}] on page '{page}': {message}")


class ValidationError(NifflerError):
    """Ошибки валидации данных"""

    def __init__(self, message: str, field: str = None, value: str = None):
        self.field = field
        self.value = value
        super().__init__(f"VALIDATION ERROR [{field}='{value}']: {message}")
