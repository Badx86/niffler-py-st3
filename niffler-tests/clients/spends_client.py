import requests
from models.data_models import Category, Spend, SpendAdd


class SpendsHttpClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def get_categories(self) -> list[Category]:
        response = self.session.get(f"{self.base_url}/api/categories/all")
        response.raise_for_status()
        return [Category.model_validate(item) for item in response.json()]

    def add_spend(self, spend: SpendAdd) -> Spend:
        response = self.session.post(f"{self.base_url}/api/spends/add", json=spend.model_dump())
        response.raise_for_status()
        return Spend.model_validate(response.json())

    def add_category(self, name: str) -> Category:
        response = self.session.post(f"{self.base_url}/api/categories/add", json={"category": name})
        response.raise_for_status()
        return Category.model_validate(response.json())

    def get_spends(self) -> list[Spend]:
        response = self.session.get(f"{self.base_url}/api/spends/all")
        response.raise_for_status()
        return [Spend.model_validate(item) for item in response.json()]

    def remove_spends(self, ids: list[str]):
        response = self.session.delete(f"{self.base_url}/api/spends/remove", params={"ids": ids})
        response.raise_for_status()

    def remove_categories(self, category_ids: list[str]):
        """Удалить несколько категорий по ID"""
        for category_id in category_ids:
            try:
                response = self.session.delete(f"{self.base_url}/api/categories/{category_id}")
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"Не удалось удалить категорию {category_id}: {e}")

    def remove_spend(self, spend_id: str):
        """Удалить одну трату по ID"""
        self.remove_spends([spend_id])
