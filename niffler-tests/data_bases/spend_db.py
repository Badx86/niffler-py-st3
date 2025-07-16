from typing import Sequence
from sqlalchemy import create_engine, Engine
from sqlmodel import Session, select
from models.data_models import Category, Spend


class SpendDb:
    def __init__(self, db_url: str):
        self.engine: Engine = create_engine(db_url)

    def get_user_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()  # type: ignore

    def get_user_spends(self, username: str) -> Sequence[Spend]:
        """Получить все траты пользователя"""
        with Session(self.engine) as session:
            statement = select(Spend).where(Spend.username == username)
            return session.exec(statement).all()  # type: ignore

    def delete_category(self, category_id: str):
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            if category:
                session.delete(category)
                session.commit()

    def delete_spend(self, spend_id: str):
        """Удалить трату по ID"""
        with Session(self.engine) as session:
            spend = session.get(Spend, spend_id)
            if spend:
                session.delete(spend)
                session.commit()

    def get_spend_by_id(self, spend_id: str) -> Spend | None:
        """Получить трату по ID"""
        with Session(self.engine) as session:
            return session.get(Spend, spend_id)
