import allure
from .base_page import BasePage


class MainPage(BasePage):
    """Главная страница приложения после входа в систему"""

    def __init__(self, page):
        super().__init__(page)

        # Ищем все элементы страницы один раз при создании объекта.

        # Основные элементы в шапке
        self.LOGO = self.page.locator('a:has-text("Niffler")')
        self.NEW_SPENDING_BUTTON = self.page.locator('a[href="/spending"]')
        self.PROFILE_BUTTON = self.page.locator('button[aria-label="Menu"]')

        # Заголовки разделов
        self.STATISTICS_TITLE = self.page.locator('h2:has-text("Statistics")')
        self.HISTORY_TITLE = self.page.locator('h2:has-text("History of Spendings")')

        # Элементы поиска
        self.SEARCH_INPUT = self.page.locator('input[placeholder="Search"]')
        self.SEARCH_BUTTON = self.page.locator('button[aria-label="search"]')

        # Фильтры
        self.TIME_FILTER_BUTTON = self.page.locator('div[id="period"]')
        self.CURRENCY_FILTER_BUTTON = self.page.locator('div[id="currency"]')
        self.DELETE_BUTTON = self.page.locator('button[id="delete"]')

        # Элементы когда нет трат
        self.NO_SPENDINGS_MESSAGE = self.page.locator('text="There are no spendings"')
        self.NIFFLER_IMAGE = self.page.locator('img[alt="Lonely niffler"]')

        # Выпадающее меню профиля
        self.PROFILE_MENU_PROFILE = self.page.locator('a[href="/profile"]')
        self.PROFILE_MENU_FRIENDS = self.page.locator('a[href="/people/friends"]')
        self.PROFILE_MENU_ALL_PEOPLE = self.page.locator('a[href="/people/all"]')
        self.PROFILE_MENU_SIGN_OUT = self.page.locator('li[role="menuitem"]:has-text("Sign out")')

        # Варианты в фильтре времени
        self.TIME_OPTION_ALL = self.page.locator('li[data-value="ALL"]')
        self.TIME_OPTION_LAST_MONTH = self.page.locator('li[data-value="MONTH"]')
        self.TIME_OPTION_LAST_WEEK = self.page.locator('li[data-value="WEEK"]')
        self.TIME_OPTION_TODAY = self.page.locator('li[data-value="TODAY"]')

        # Варианты в фильтре валют
        self.CURRENCY_OPTION_ALL = self.page.locator('li[data-value="ALL"]')
        self.CURRENCY_OPTION_RUB = self.page.locator('li[data-value="RUB"]')
        self.CURRENCY_OPTION_KZT = self.page.locator('li[data-value="KZT"]')
        self.CURRENCY_OPTION_EUR = self.page.locator('li[data-value="EUR"]')
        self.CURRENCY_OPTION_USD = self.page.locator('li[data-value="USD"]')

    def is_loaded(self):
        """
        Проверяем что мы действительно на главной странице
        Смотрим на URL и заголовок страницы
        """
        current_url = self.page.url
        title = self.page.title()
        is_correct_url = "frontend.niffler.dc" in current_url and "/main" in current_url
        is_correct_title = title == "Niffler"
        return is_correct_url and is_correct_title
