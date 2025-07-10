import allure
from .base_page import BasePage
from playwright.sync_api import Page


class SpendingPage(BasePage):
    """Страница расходов"""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Открытие страницы добавления расходов")
    def open(self) -> None:
        """Переход на страницу добавления расходов"""
        self.navigate_to("http://frontend.niffler.dc/spending")

    def is_loaded(self) -> bool:
        """Проверка что страница загружена"""
        return "/spending" in self.page.url
