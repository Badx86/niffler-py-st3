import allure
from pages.login_page import LoginPage


@allure.feature("Авторизация")
class TestAuth:
    """Тесты для проверки входа в систему и регистрации"""

    @allure.story("Успешная регистрация")
    def test_successful_registration(self, page, user_data):
        """Проверяем что новый пользователь может зарегистрироваться"""
        username, password = user_data
        login_page = LoginPage(page)

        # Идем на страницу регистрации
        login_page.open()
        login_page.click_create_account_button()
        assert login_page.is_on_register_page()

        # Заполняем форму регистрации
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.fill('input[name="passwordSubmit"]', password)
        page.click('button:has-text("Sign Up")')

        # Проверяем что регистрация прошла успешно
        assert "/register" in page.url
        assert page.locator('text="Congratulations! You\'ve registered!"').is_visible()
        assert page.locator("a.form_sign-in").is_visible()

    @allure.story("Неуспешная авторизация")
    def test_failed_login(self, page, user_data):
        """Проверяем что с невалидными данными нельзя авторизоваться"""
        username, password = user_data
        login_page = LoginPage(page)

        # Пытаемся войти с несуществующими данными
        login_page.open()
        login_page.enter_username(username)
        login_page.enter_password(password)
        login_page.click_login_button()

        # Должна появиться ошибка
        assert login_page.is_error_displayed()

    @allure.story("Переход к регистрации")
    def test_go_to_registration(self, page):
        """Проверяем что со страницы входа можно перейти к регистрации"""
        login_page = LoginPage(page)

        # Переходим к регистрации
        login_page.open()
        login_page.click_create_account_button()
        assert login_page.is_on_register_page()

        # Проверяем что все элементы формы регистрации на месте
        assert page.locator("h1.header").is_visible()
        assert page.locator("a.form__link").is_visible()
        assert page.locator('input[name="username"]').is_visible()
        assert page.locator('input[name="password"]').is_visible()
        assert page.locator('input[name="passwordSubmit"]').is_visible()
        assert page.locator("button.form__submit").is_visible()
