from typing import Sequence
from sqlalchemy import create_engine, Engine
from sqlmodel import Session, select
from models.data_models import Category, Spend
from exceptions import DatabaseError


class SpendDb:
    def __init__(self, db_url: str):
        try:
            self.engine: Engine = create_engine(db_url)
        except Exception as e:
            raise DatabaseError(f"Не удалось подключиться к БД: {str(e)}", operation="connect")

    def get_user_categories(self, username: str) -> Sequence[Category]:
        try:
            with Session(self.engine) as session:
                statement = select(Category).where(Category.username == username)
                return session.exec(statement).all()  # type: ignore
        except Exception as e:
            raise DatabaseError(
                f"Ошибка получения категорий: {str(e)}",
                username=username,
                operation="get_categories"
            )

    def get_user_spends(self, username: str) -> Sequence[Spend]:
        """Получить все траты пользователя"""
        try:
            with Session(self.engine) as session:
                statement = select(Spend).where(Spend.username == username)
                return session.exec(statement).all()  # type: ignore
        except Exception as e:
            raise DatabaseError(
                f"Ошибка получения трат: {str(e)}",
                username=username,
                operation="get_spends"
            )

    def delete_category(self, category_id: str, username: str = None):
        try:
            with Session(self.engine) as session:
                category = session.get(Category, category_id)
                if category:
                    session.delete(category)
                    session.commit()
                else:
                    raise DatabaseError(
                        f"Категория с ID {category_id} не найдена",
                        username=username,
                        operation="delete_category"
                    )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                f"Ошибка удаления категории {category_id}: {str(e)}",
                username=username,
                operation="delete_category"
            )

    def delete_spend(self, spend_id: str, username: str = None):
        """Удалить трату по ID"""
        try:
            with Session(self.engine) as session:
                spend = session.get(Spend, spend_id)
                if spend:
                    session.delete(spend)
                    session.commit()
                else:
                    raise DatabaseError(
                        f"Трата с ID {spend_id} не найдена",
                        username=username,
                        operation="delete_spend"
                    )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                f"Ошибка удаления траты {spend_id}: {str(e)}",
                username=username,
                operation="delete_spend"
            )

    def get_spend_by_id(self, spend_id: str) -> Spend | None:
        """Получить трату по ID"""
        try:
            with Session(self.engine) as session:
                return session.get(Spend, spend_id)
        except Exception as e:
            raise DatabaseError(
                f"Ошибка получения траты по ID {spend_id}: {str(e)}",
                operation="get_spend_by_id"
            )
