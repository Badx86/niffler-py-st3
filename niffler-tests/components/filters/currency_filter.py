import allure
from playwright.sync_api import Page


class CurrencyFilterComponent:
    """Компонент фильтра по валютам для трат"""

    def __init__(self, page: Page) -> None:
        self.page = page

        # Фильтр валют
        self.CURRENCY_FILTER_BUTTON = self.page.locator('div[id="currency"]')

        # Варианты в фильтре валют
        self.CURRENCY_OPTION_ALL = self.page.locator('li[data-value="ALL"]')
        self.CURRENCY_OPTION_RUB = self.page.locator('li[data-value="RUB"]')
        self.CURRENCY_OPTION_KZT = self.page.locator('li[data-value="KZT"]')
        self.CURRENCY_OPTION_EUR = self.page.locator('li[data-value="EUR"]')
        self.CURRENCY_OPTION_USD = self.page.locator('li[data-value="USD"]')

    @allure.step("Открытие фильтра валют")
    def open_filter(self) -> None:
        """Открытие выпадающего списка фильтра валют"""
        self.CURRENCY_FILTER_BUTTON.click()

    @allure.step("Выбор валюты: {currency}")
    def select_currency(self, currency: str) -> None:
        """Выбор конкретной валюты из фильтра"""
        self.open_filter()
        currency_option = self.page.locator(f'li[data-value="{currency}"]')
        currency_option.click()

    def are_all_options_visible(self) -> bool:
        """Проверка что все опции фильтра валют видны"""
        return (
            self.CURRENCY_OPTION_ALL.is_visible()
            and self.CURRENCY_OPTION_RUB.is_visible()
            and self.CURRENCY_OPTION_KZT.is_visible()
            and self.CURRENCY_OPTION_EUR.is_visible()
            and self.CURRENCY_OPTION_USD.is_visible()
        )
