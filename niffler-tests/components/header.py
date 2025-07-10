import allure
from playwright.sync_api import Page


class HeaderComponent:
    """Компонент шапки приложения с логотипом, навигацией и профилем"""

    def __init__(self, page: Page) -> None:
        self.page = page

        # Основные элементы в шапке
        # self.LOGO = self.page.locator('h1:has-text("Niffler")')
        self.LOGO = self.page.locator('a.link[href="/main"] img')
        self.NEW_SPENDING_BUTTON = self.page.locator('a[href="/spending"]')
        self.PROFILE_BUTTON = self.page.locator('button[aria-label="Menu"]')

        # Выпадающее меню профиля
        self.PROFILE_MENU_PROFILE = self.page.locator('a[href="/profile"]')
        self.PROFILE_MENU_FRIENDS = self.page.locator('a[href="/people/friends"]')
        self.PROFILE_MENU_ALL_PEOPLE = self.page.locator('a[href="/people/all"]')
        self.PROFILE_MENU_SIGN_OUT = self.page.locator(
            'li[role="menuitem"]:has-text("Sign out")'
        )

    @allure.step("Клик по кнопке New spending")
    def click_new_spending(self) -> None:
        """Переход к созданию новой траты"""
        self.NEW_SPENDING_BUTTON.click()

    @allure.step("Открытие меню профиля")
    def open_profile_menu(self) -> None:
        """Открытие выпадающего меню профиля"""
        self.PROFILE_BUTTON.click()

    def is_logo_visible(self) -> bool:
        """Проверка видимости логотипа"""
        return self.LOGO.is_visible()

    def is_new_spending_button_visible(self) -> bool:
        """Проверка видимости кнопки создания траты"""
        return self.NEW_SPENDING_BUTTON.is_visible()

    def is_profile_button_visible(self) -> bool:
        """Проверка видимости кнопки профиля"""
        return self.PROFILE_BUTTON.is_visible()

    def is_profile_menu_visible(self) -> bool:
        """Проверка что все пункты меню профиля видимы"""
        return (
            self.PROFILE_MENU_PROFILE.is_visible()
            and self.PROFILE_MENU_FRIENDS.is_visible()
            and self.PROFILE_MENU_ALL_PEOPLE.is_visible()
            and self.PROFILE_MENU_SIGN_OUT.is_visible()
        )
