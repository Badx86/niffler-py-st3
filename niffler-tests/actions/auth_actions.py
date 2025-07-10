import allure
from pages.login_page import LoginPage
from components.forms.login_form import LoginFormComponent


class AuthActions:
    """Действия для работы с авторизацией и регистрацией пользователей"""

    def __init__(self, login_page: LoginPage) -> None:
        self.login_page = login_page
        self.page = login_page.page  # Получаем page внутри класса
        self.login_form = LoginFormComponent(self.page)

    @allure.step("Регистрация пользователя")
    def register_user(self, username: str, password: str) -> bool:
        """
        Регистрация нового пользователя и возврат результата

        Args:
            username: имя пользователя
            password: пароль

        Returns:
            bool: успешность регистрации
        """
        # Идем на страницу регистрации и заполняем форму
        self.login_page.open()
        self.login_form.click_create_account()

        self.login_form.enter_username(username)
        self.login_form.enter_password(password)
        self.login_form.enter_password_submit(password)
        self.login_form.click_signup()

        return self.login_form.is_success_message_displayed()

    @allure.step("Вход в систему")
    def login_user(self, username: str, password: str) -> bool:
        """
        Авторизация пользователя и переход на главную страницу

        Args:
            username: имя пользователя
            password: пароль

        Returns:
            bool: успешность входа
        """
        # Входим в систему с данными
        self.login_page.open()
        self.login_form.enter_username(username)
        self.login_form.enter_password(password)
        self.login_form.click_login()

        # Ждем пока нас перебросит на главную страницу
        self.page.wait_for_url("**/main", timeout=5000)
        return "/main" in self.page.url

    @allure.step("Попытка входа с неверными данными")
    def try_invalid_login(self, username: str, password: str) -> bool:
        """
        Попытка входа с несуществующими/неверными данными

        Args:
            username: имя пользователя
            password: пароль

        Returns:
            bool: отображается ли ошибка
        """
        # Пытаемся войти с несуществующими данными
        self.login_page.open()
        self.login_form.enter_username(username)
        self.login_form.enter_password(password)
        self.login_form.click_login()

        # Должна появиться ошибка
        return self.login_form.is_error_displayed()

    @allure.step("Переход к регистрации")
    def go_to_registration(self) -> bool:
        """
        Переход со страницы входа к регистрации

        Returns:
            bool: находимся ли на странице регистрации
        """
        # Переходим к регистрации
        self.login_page.open()
        self.login_form.click_create_account()

        return self.login_page.is_on_register_page()
