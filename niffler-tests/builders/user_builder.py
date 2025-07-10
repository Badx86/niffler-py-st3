from mimesis import Person


class UserBuilder:
    """Билдер для создания тестовых данных пользователей"""

    def __init__(self):
        self.person = Person()
        self._username = None
        self._password = None

    def with_random_credentials(self):
        """Генерация случайных учетных данных"""
        self._username = self.person.username() + str(self.person.identifier(mask="###"))
        self._password = self.person.password(length=10)
        return self

    def with_username(self, username):
        """Установка конкретного имени пользователя"""
        self._username = username
        return self

    def with_password(self, password):
        """Установка конкретного пароля"""
        self._password = password
        return self

    def build(self):
        """
        Создание объекта пользователя с данными

        Returns:
            dict: словарь с данными пользователя
        """
        # Если данные не заданы, генерируем случайные
        if not self._username:
            self._username = self.person.username() + str(self.person.identifier(mask="###"))
        if not self._password:
            self._password = self.person.password(length=10)

        return {
            'username': self._username,
            'password': self._password
        }
