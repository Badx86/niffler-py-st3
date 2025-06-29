import allure
from pages.login_page import LoginPage
from pages.main_page import MainPage
from utils.urls import REGISTER_ENDPOINT


@allure.feature("Авторизация")
class TestAuth:

    @allure.story("Успешная регистрация")
    def test_successful_registration(self, page, user_data):
        """Тест регистрации нового пользователя"""
        login_page = LoginPage(page)
        username, password = user_data

        with allure.step("Переход на страницу регистрации"):
            login_page.open()
            login_page.click_create_account_button()
            login_page.assert_on_register_page()

        with allure.step("Заполнение формы регистрации"):
            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', password)
            page.fill('input[name="passwordSubmit"]', password)
            page.click('button:has-text("Sign Up")')

        with allure.step("Проверка успешной регистрации"):
            assert REGISTER_ENDPOINT in page.url, f"Должны быть на {REGISTER_ENDPOINT}"
            assert page.locator('text="Congratulations! You\'ve registered!"').is_visible()
            assert page.locator('a.form_sign-in').is_visible()

    @allure.story("Неуспешная авторизация")
    def test_failed_login(self, page, user_data):
        """Тест неуспешной авторизации"""
        login_page = LoginPage(page)
        username, password = user_data

        with allure.step("Попытка логина с несуществующими данными"):
            login_page.open()
            login_page.enter_username(username)
            login_page.enter_password(password)
            login_page.click_login_button()

        with allure.step("Проверка ошибки авторизации"):
            login_page.assert_login_error()

    @allure.story("Переход к регистрации")
    def test_go_to_registration(self, page):
        """Тест перехода к странице регистрации"""
        login_page = LoginPage(page)

        with allure.step("Переход на страницу регистрации"):
            login_page.open()
            login_page.click_create_account_button()
            login_page.assert_on_register_page()

        with allure.step("Проверка элементов формы регистрации"):
            # Проверка заголовка по классу
            assert page.locator('h1.header').is_visible()

            # Проверка ссылки "Log in!"
            assert page.locator('a.form__link').is_visible()

            # Проверка поля Username и плейсхолдера
            username_field = page.locator('input[name="username"]')
            assert username_field.is_visible()
            assert username_field.get_attribute('placeholder') == "Type your username"

            # Проверка поля Password и плейсхолдера
            password_field = page.locator('input[name="password"]')
            assert password_field.is_visible()
            assert password_field.get_attribute('placeholder') == "Type your password"

            # Проверка поля Submit password и плейсхолдера
            submit_password_field = page.locator('input[name="passwordSubmit"]')
            assert submit_password_field.is_visible()
            assert submit_password_field.get_attribute('placeholder') == "Submit your password"

            # Проверка кнопки Sign Up по классу
            assert page.locator('button.form__submit').is_visible()
