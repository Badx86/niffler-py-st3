import allure
from .base_page import BasePage
from playwright.sync_api import Page


class LoginPage(BasePage):
    """Страница входа в систему"""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Открытие страницы логина")
    def open(self) -> None:
        """Переходим на страницу входа"""
        self.navigate_to("http://auth.niffler.dc:9000/login")

    def is_loaded(self) -> bool:
        """Проверяем что мы действительно на странице входа"""
        return "/login" in self.page.url

    def is_on_register_page(self) -> bool:
        """Проверяем что попали на страницу регистрации"""
        return "/register" in self.page.url
