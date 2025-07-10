from pydantic import BaseModel


class UserData(BaseModel):
    """Модель данных пользователя"""

    username: str
    password: str


class SpendingData(BaseModel):
    """Модель данных траты"""

    amount: int | float
    currency: str  # RUB, USD, EUR, KZT
    category: str
    description: str
