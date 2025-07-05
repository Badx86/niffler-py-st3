import allure
from .base_page import BasePage
from utils.urls import AUTH_BASE_URL, LOGIN_ENDPOINT


class LoginPage(BasePage):
    """Страница авторизации"""

    # Селекторы
    USERNAME_INPUT = 'input[name="username"]'
    PASSWORD_INPUT = 'input[name="password"]'
    LOGIN_BUTTON = 'button:has-text("Log in")'
    CREATE_ACCOUNT_BUTTON = 'a:has-text("Create new account")'
    ERROR_MESSAGE = '[class*="error"], [class*="alert"], .alert-danger'

    @allure.step("Открытие страницы логина")
    def open(self):
        """Открыть страницу логина"""
        self.go_to(f"{AUTH_BASE_URL}{LOGIN_ENDPOINT}")

    @allure.step("Ввод логина: {username}")
    def enter_username(self, username):
        """Ввести имя пользователя"""
        self.find_element(self.USERNAME_INPUT).fill(username)

    @allure.step("Ввод пароля")
    def enter_password(self, password):
        """Ввести пароль"""
        self.find_element(self.PASSWORD_INPUT).fill(password)

    @allure.step("Клик по кнопке Log in")
    def click_login_button(self):
        """Кликнуть по кнопке входа"""
        self.find_element(self.LOGIN_BUTTON).click()

    @allure.step("Клик по кнопке Create new account")
    def click_create_account_button(self):
        """Кликнуть по кнопке создания аккаунта"""
        self.find_element(self.CREATE_ACCOUNT_BUTTON).click()

    @allure.step("Проверка что находимся на странице логина")
    def assert_on_login_page(self):
        """Проверить что находимся на странице логина"""
        assert LOGIN_ENDPOINT in self.page.url, f"Не на странице логина. URL: {self.page.url}"

    @allure.step("Проверка ошибки логина")
    def assert_login_error(self):
        """Проверить ошибку логина"""
        assert "?error" in self.page.url, "В URL нет параметра error"
        assert self.page.locator('.form__error-container').is_visible(), "Контейнер ошибки не видим"

    @allure.step("Проверка что находимся на странице регистрации")
    def assert_on_register_page(self):
        """Проверить что находимся на странице регистрации"""
        assert "/register" in self.page.url, f"Не на странице регистрации. URL: {self.page.url}"

    @allure.step("Проверка отображения ошибки")
    def is_error_displayed(self):
        """Проверить отображение ошибки"""
        try:
            return self.find_element(self.ERROR_MESSAGE).is_visible()
        except:
            return False