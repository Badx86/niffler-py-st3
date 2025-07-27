import allure
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

    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Базовый метод для HTTP запросов с attachments"""
        url = f"{self.base_url}{endpoint}"

        with allure.step(f"{method.upper()} {endpoint}"):
            allure.attach(url, name="URL", attachment_type=allure.attachment_type.TEXT)

            if 'json' in kwargs:
                allure.attach(str(kwargs['json']), name="Request Body", attachment_type=allure.attachment_type.JSON)

            response = self.session.request(method, url, **kwargs)

            allure.attach(str(response.status_code), name="Status", attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.text, name="Response", attachment_type=allure.attachment_type.JSON)

            response.raise_for_status()
            return response

    @allure.step("Получение всех категорий")
    def get_categories(self) -> list[Category]:
        response = self._make_request("GET", "/api/categories/all")
        return [Category.model_validate(item) for item in response.json()]

    @allure.step("Добавление траты")
    def add_spend(self, spend: SpendAdd) -> Spend:
        response = self._make_request("POST", "/api/spends/add", json=spend.model_dump())
        return Spend.model_validate(response.json())

    @allure.step("Добавление категории: {name}")
    def add_category(self, name: str) -> Category:
        response = self._make_request("POST", "/api/categories/add", json={"category": name})
        return Category.model_validate(response.json())

    @allure.step("Получение всех трат")
    def get_spends(self) -> list[Spend]:
        response = self._make_request("GET", "/api/spends/all")
        return [Spend.model_validate(item) for item in response.json()]

    @allure.step("Удаление трат: {ids}")
    def remove_spends(self, ids: list[str]):
        self._make_request("DELETE", "/api/spends/remove", params={"ids": ids})

    @allure.step("Удаление категорий: {category_ids}")
    def remove_categories(self, category_ids: list[str]):
        for category_id in category_ids:
            try:
                self._make_request("DELETE", f"/api/categories/{category_id}")
            except requests.exceptions.HTTPError as e:
                allure.attach(f"Ошибка удаления {category_id}: {e}", name="Error",
                              attachment_type=allure.attachment_type.TEXT)

    @allure.step("Удаление траты: {spend_id}")
    def remove_spend(self, spend_id: str):
        """Удалить одну трату по ID"""
        self.remove_spends([spend_id])