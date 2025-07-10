import allure
from typing import Any
from components.header import HeaderComponent


class ProfileActions:
    """Действия для работы с профилем пользователя"""

    def __init__(self, page_object: Any) -> None:
        self.page = page_object.page
        self.header = HeaderComponent(self.page)

    @allure.step("Открытие меню профиля")
    def open_profile_menu(self) -> bool:
        """
        Открытие выпадающего меню профиля

        Returns:
            bool: отображается ли меню профиля
        """
        self.header.open_profile_menu()
        return self.header.is_profile_menu_visible()

    @allure.step("Переход в профиль")
    def go_to_profile(self) -> None:
        """Переход на страницу профиля пользователя"""
        self.header.open_profile_menu()
        self.header.PROFILE_MENU_PROFILE.click()

    @allure.step("Переход к друзьям")
    def go_to_friends(self) -> None:
        """Переход на страницу друзей"""
        self.header.open_profile_menu()
        self.header.PROFILE_MENU_FRIENDS.click()

    @allure.step("Переход ко всем людям")
    def go_to_all_people(self) -> None:
        """Переход на страницу всех пользователей"""
        self.header.open_profile_menu()
        self.header.PROFILE_MENU_ALL_PEOPLE.click()

    @allure.step("Выход из системы")
    def logout(self) -> None:
        """Выход из системы"""
        self.header.open_profile_menu()
        self.header.PROFILE_MENU_SIGN_OUT.click()
