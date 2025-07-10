import allure
from .base_page import BasePage


class LoginPage(BasePage):
    """Страница входа в систему"""

    def __init__(self, page):
        super().__init__(page)

    @allure.step("Открытие страницы логина")
    def open(self):
        """Переходим на страницу входа"""
        self.navigate_to("http://auth.niffler.dc:9000/login")

    def is_loaded(self):
        """Проверяем что мы действительно на странице входа"""
        return "/login" in self.page.url

    def is_on_register_page(self):
        """Проверяем что попали на страницу регистрации"""
        return "/register" in self.page.url
