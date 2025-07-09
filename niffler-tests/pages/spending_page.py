import allure
from .base_page import BasePage


class SpendingPage(BasePage):
    """Страница расходов"""

    def __init__(self, page):
        super().__init__(page)

    @allure.step("Открытие страницы добавления расходов")
    def open(self):
        """Переход на страницу добавления расходов"""
        self.navigate_to("http://frontend.niffler.dc/spending")

    def is_loaded(self):
        """Проверка что страница загружена"""
        return "/spending" in self.page.url
