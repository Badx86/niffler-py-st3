import allure
from .base_page import BasePage


class LoginPage(BasePage):
    """Страница входа в систему"""

    def __init__(self, page):
        super().__init__(page)

        # Находим все нужные элементы один раз при создании объекта
        self.username_input = self.page.locator('input[name="username"]')
        self.password_input = self.page.locator('input[name="password"]')
        self.login_button = self.page.locator('button:has-text("Log in")')
        self.create_account_button = self.page.locator(
            'a:has-text("Create new account")'
        )
        self.error_message = self.page.locator(
            '[class*="error"], [class*="alert"], .alert-danger'
        )

    @allure.step("Открытие страницы логина")
    def open(self):
        """Переходим на страницу входа"""
        self.navigate_to("http://auth.niffler.dc:9000/login")

    @allure.step("Ввод логина: {username}")
    def enter_username(self, username):
        """Вводим имя пользователя"""
        self.username_input.fill(username)

    @allure.step("Ввод пароля")
    def enter_password(self, password):
        """Вводим пароль"""
        self.password_input.fill(password)

    @allure.step("Клик по кнопке Log in")
    def click_login_button(self):
        """Нажимаем кнопку входа"""
        self.login_button.click()

    @allure.step("Клик по кнопке Create new account")
    def click_create_account_button(self):
        """Нажимаем кнопку создания нового аккаунта"""
        self.create_account_button.click()

    def is_loaded(self):
        """Проверяем что мы действительно на странице входа"""
        return "/login" in self.page.url and self.username_input.is_visible()

    def is_error_displayed(self):
        """Проверяем появилась ли ошибка при входе"""
        return (
            "?error" in self.page.url
            and self.page.locator(".form__error-container").is_visible()
        )

    def is_on_register_page(self):
        """Проверяем что попали на страницу регистрации"""
        return "/register" in self.page.url
