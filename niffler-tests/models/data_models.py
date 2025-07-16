from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from datetime import date


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


# SQLModel модели для БД
class Category(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    username: str
    archived: bool = False


class Spend(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    spend_date: date
    currency: str
    amount: float
    description: str
    category_id: str


class SpendAdd(SQLModel):
    amount: float
    description: str
    category: str
    spendDate: str
    currency: str
