import random
from mimesis import Text


class SpendingBuilder:
    """Билдер для создания тестовых данных трат"""

    def __init__(self):
        self.text = Text()
        self._amount = None
        self._currency = None
        self._category = None
        self._description = None

    def with_amount(self, amount):
        """Установка конкретной суммы"""
        self._amount = amount
        return self

    def with_random_amount(self, min_amount=1, max_amount=10000):
        """Генерация случайной суммы в заданном диапазоне"""
        self._amount = random.randint(min_amount, max_amount)
        return self

    def with_currency(self, currency):
        """Установка конкретной валюты"""
        self._currency = currency
        return self

    def with_random_currency(self):
        """Выбор случайной валюты из доступных"""
        currencies = ["RUB", "USD", "EUR", "KZT"]
        self._currency = random.choice(currencies)
        return self

    def with_category(self, category):
        """Установка конкретной категории"""
        self._category = category
        return self

    def with_random_category(self):
        """Выбор случайной категории из популярных"""
        categories = ["Food", "Transport", "Entertainment", "Shopping", "Health", "Bills"]
        self._category = random.choice(categories)
        return self

    def with_description(self, description):
        """Установка конкретного описания"""
        self._description = description
        return self

    def with_random_description(self):
        """Генерация случайного описания из типичных трат"""
        descriptions = [
            "Lunch at restaurant",
            "Coffee break",
            "Grocery shopping",
            "Bus ticket",
            "Movie theater",
            "Online purchase",
            "Pharmacy",
            "Utility bill"
        ]
        self._description = random.choice(descriptions)
        return self

    def build(self):
        """
        Создание объекта траты с данными

        Returns:
            dict: словарь с данными траты
        """
        # Если данные не заданы, генерируем дефолтные/случайные
        if self._amount is None:
            self._amount = random.randint(100, 5000)
        if self._currency is None:
            self._currency = random.choice(["RUB", "USD", "EUR", "KZT"])
        if self._category is None:
            self._category = random.choice(["Food", "Transport", "Entertainment"])
        if self._description is None:
            self._description = "Test spending"

        return {
            'amount': self._amount,
            'currency': self._currency,
            'category': self._category,
            'description': self._description
        }
