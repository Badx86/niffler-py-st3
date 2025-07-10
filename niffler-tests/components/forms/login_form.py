import allure
from playwright.sync_api import Page


class LoginFormComponent:
    """Компонент формы авторизации и регистрации"""

    def __init__(self, page: Page) -> None:
        self.page = page

        # Находим все нужные элементы один раз при создании объекта
        self.username_input = self.page.locator('input[name="username"]')
        self.password_input = self.page.locator('input[name="password"]')
        self.password_submit_input = self.page.locator('input[name="passwordSubmit"]')
        self.login_button = self.page.locator('button:has-text("Log in")')
        self.signup_button = self.page.locator('button:has-text("Sign Up")')
        self.create_account_button = self.page.locator(
            'a:has-text("Create new account")'
        )
        self.error_message = self.page.locator(
            '[class*="error"], [class*="alert"], .alert-danger'
        )

    @allure.step("Ввод логина: {username}")
    def enter_username(self, username: str) -> None:
        """Вводим имя пользователя"""
        self.username_input.fill(username)

    @allure.step("Ввод пароля")
    def enter_password(self, password: str) -> None:
        """Вводим пароль"""
        self.password_input.fill(password)

    @allure.step("Ввод подтверждения пароля")
    def enter_password_submit(self, password: str) -> None:
        """Вводим подтверждение пароля при регистрации"""
        self.password_submit_input.fill(password)

    @allure.step("Клик по кнопке Log in")
    def click_login(self) -> None:
        """Нажимаем кнопку входа"""
        self.login_button.click()

    @allure.step("Клик по кнопке Sign Up")
    def click_signup(self) -> None:
        """Нажимаем кнопку регистрации"""
        self.signup_button.click()

    @allure.step("Клик по кнопке Create new account")
    def click_create_account(self) -> None:
        """Нажимаем кнопку создания нового аккаунта"""
        self.create_account_button.click()

    def is_error_displayed(self) -> bool:
        """Проверяем появилась ли ошибка при входе"""
        return (
            "?error" in self.page.url
            and self.page.locator(".form__error-container").is_visible()
        )

    def is_success_message_displayed(self) -> bool:
        """Проверяем появилось ли сообщение об успешной регистрации"""
        return self.page.locator(
            'text="Congratulations! You\'ve registered!"'
        ).is_visible()
