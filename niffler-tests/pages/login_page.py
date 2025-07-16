import allure
from .base_page import BasePage
from playwright.sync_api import Page
from typing import Any
from config import Config


class LoginPage(BasePage):
    """Страница входа в систему"""

    def __init__(self, page: Page, environment: dict[str, Any] = None) -> None:
        super().__init__(page, environment)

    @allure.step("Открытие страницы логина")
    def open(self) -> None:
        """Переходим на страницу входа"""
        login_url = self.get_full_url("auth_url", Config.LOGIN_ENDPOINT)
        self.navigate_to(login_url)

    def is_loaded(self) -> bool:
        """Проверяем что мы действительно на странице входа"""
        return "/login" in self.page.url

    def is_on_register_page(self) -> bool:
        """Проверяем что попали на страницу регистрации"""
        return "/register" in self.page.url
