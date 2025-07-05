import allure
from .base_page import BasePage


class MainPage(BasePage):
    """Главная страница после авторизации"""

    # Основные элементы
    LOGO = 'a:has-text("Niffler")'
    NEW_SPENDING_BUTTON = 'a[href="/spending"]'  # Ссылка New spending
    PROFILE_BUTTON = 'button[aria-label="Menu"]'  # Круглая кнопка профиля

    # Заголовки
    STATISTICS_TITLE = 'h2:has-text("Statistics")'
    HISTORY_TITLE = 'h2:has-text("History of Spendings")'

    # Поиск
    SEARCH_INPUT = 'input[placeholder="Search"]'
    SEARCH_BUTTON = 'button[aria-label="search"]'

    # Фильтры
    TIME_FILTER_BUTTON = 'div[id="period"]'  # Комбобокс фильтра времени
    CURRENCY_FILTER_BUTTON = 'div[id="currency"]'  # Комбобокс фильтра валют
    DELETE_BUTTON = 'button[id="delete"]'  # Кнопка Delete

    # Дефолтное состояние
    NO_SPENDINGS_MESSAGE = 'text="There are no spendings"'
    NIFFLER_IMAGE = 'img[alt="Lonely niffler"]'

    # Меню профиля (выпадающий список)
    PROFILE_MENU_PROFILE = 'a[href="/profile"]'
    PROFILE_MENU_FRIENDS = 'a[href="/people/friends"]'
    PROFILE_MENU_ALL_PEOPLE = 'a[href="/people/all"]'
    PROFILE_MENU_SIGN_OUT = 'li[role="menuitem"]:has-text("Sign out")'

    # Опции фильтра времени
    TIME_OPTION_ALL = 'li[data-value="ALL"]'
    TIME_OPTION_LAST_MONTH = 'li[data-value="MONTH"]'
    TIME_OPTION_LAST_WEEK = 'li[data-value="WEEK"]'
    TIME_OPTION_TODAY = 'li[data-value="TODAY"]'

    # Опции фильтра валют
    CURRENCY_OPTION_ALL = 'li[data-value="ALL"]'
    CURRENCY_OPTION_RUB = 'li[data-value="RUB"]'
    CURRENCY_OPTION_KZT = 'li[data-value="KZT"]'
    CURRENCY_OPTION_EUR = 'li[data-value="EUR"]'
    CURRENCY_OPTION_USD = 'li[data-value="USD"]'

    @allure.step("Проверка нахождения на главной странице")
    def is_on_main_page(self):
        """Проверка нахождения на главной странице"""
        current_url = self.page.url
        title = self.get_title()

        is_correct_url = "frontend.niffler.dc" in current_url and "/main" in current_url
        is_correct_title = title == "Niffler"

        return is_correct_url and is_correct_title
