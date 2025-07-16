import allure
from .base_page import BasePage
from playwright.sync_api import Page
from typing import Any


class SpendingPage(BasePage):
    """Страница расходов"""

    def __init__(self, page: Page, environment: dict[str, Any] = None) -> None:
        super().__init__(page, environment)

    @allure.step("Открытие страницы добавления расходов")
    def open(self) -> None:
        """Переход на страницу добавления расходов"""
        spending_url = self.get_full_url("frontend_url", "/spending")
        self.navigate_to(spending_url)

    def is_loaded(self) -> bool:
        """Проверка что страница загружена"""
        return "/spending" in self.page.url
