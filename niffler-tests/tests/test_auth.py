import allure
from actions.auth_actions import AuthActions


@allure.feature("Авторизация")
class TestAuth:
    """Тесты для проверки входа в систему и регистрации"""

    @allure.story("Успешная регистрация")
    def test_successful_registration(self, login_page, user_data):
        """Проверяем что новый пользователь может зарегистрироваться"""
        auth_actions = AuthActions(login_page)

        success = auth_actions.register_user(user_data.username, user_data.password)
        assert success, "Регистрация не прошла успешно"

    @allure.story("Неуспешная авторизация")
    def test_failed_login(self, login_page, user_data):
        """Проверяем что с невалидными данными нельзя авторизоваться"""
        auth_actions = AuthActions(login_page)

        error_displayed = auth_actions.try_invalid_login(
            user_data.username, user_data.password
        )
        assert error_displayed, "Ошибка авторизации не отображается"

    @allure.story("Переход к регистрации")
    def test_go_to_registration(self, login_page):
        """Проверяем что со страницы входа можно перейти к регистрации"""
        auth_actions = AuthActions(login_page)

        on_register_page = auth_actions.go_to_registration()
        assert on_register_page, "Не перешли на страницу регистрации"
