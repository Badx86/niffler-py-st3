import allure
from datetime import datetime
from playwright.sync_api import Page, Locator


class SpendingFormComponent:
    """Компонент формы создания трат"""

    def __init__(self, page: Page) -> None:
        self.page = page

        # Заголовок и навигация
        self.PAGE_TITLE = self.page.get_by_text("Add new spending")
        self.LOGO = self.page.get_by_text("Niffler")

        # Поля формы
        self.AMOUNT_INPUT = self.page.locator('input[name="amount"]')
        self.CURRENCY_DROPDOWN = self.page.locator("#currency")
        self.CATEGORY_INPUT = self.page.locator('input[name="category"]')
        self.DATE_INPUT = self.page.locator('input[name="date"]')
        self.DATE_PICKER_BUTTON = self.page.locator('button:has(img[alt="Calendar"])')
        self.DESCRIPTION_INPUT = self.page.locator('input[name="description"]')

        # Кнопки
        self.CANCEL_BUTTON = self.page.get_by_role("button", name="Cancel")
        self.ADD_BUTTON = self.page.get_by_role("button", name="Add")

        # Сообщения об ошибках валидации
        self.AMOUNT_ERROR = self.page.locator('text="Amount has to be not less then 0.01"')
        self.CATEGORY_ERROR = self.page.locator('text="Please choose category"')
        self.ERROR_MESSAGES = self.page.locator('.input__helper-text, span[class*="helper-text"]')

        # Валюты в dropdown
        self.CURRENCY_RUB = self.page.locator('li[data-value="RUB"]')
        self.CURRENCY_KZT = self.page.locator('li[data-value="KZT"]')
        self.CURRENCY_EUR = self.page.locator('li[data-value="EUR"]')
        self.CURRENCY_USD = self.page.locator('li[data-value="USD"]')

        # Календарь
        self.CALENDAR = self.page.locator(".MuiDateCalendar-root")

    def get_current_month_year(self) -> str:
        """Получение текущего месяца и года для календаря"""
        current_date = datetime.now()
        return current_date.strftime("%B %Y")  # "July 2025"

    def get_current_date_formatted(self) -> str:
        """Получение текущей даты в формате MM/DD/YYYY для проверки дефолтного значения"""
        current_date = datetime.now()
        return current_date.strftime("%m/%d/%Y")  # "07/06/2025"

    def get_calendar_month_locator(self) -> Locator:
        """Локатор для текущего месяца в календаре"""
        month_year = self.get_current_month_year()
        return self.page.locator(f'text="{month_year}"')

    @allure.step("Заполнение суммы: {amount}")
    def fill_amount(self, amount: int | float) -> None:
        """Ввод суммы"""
        self.AMOUNT_INPUT.clear()
        self.AMOUNT_INPUT.fill(str(amount))

    @allure.step("Выбор валюты: {currency}")
    def select_currency(self, currency: str) -> None:
        """Выбор валюты из dropdown"""
        self.CURRENCY_DROPDOWN.click()
        currency_option = self.page.locator(f'li[data-value="{currency}"]')
        currency_option.click()

    @allure.step("Ввод категории: {category}")
    def fill_category(self, category: str) -> None:
        """Ввод категории"""
        try:
            self.CATEGORY_INPUT.fill(category, timeout=3000)
        except:
            # Если поле заблокировано - ничего не делаем
            allure.attach("Поле категории заблокировано", name="Category Blocked")

    @allure.step("Ввод описания: {description}")
    def fill_description(self, description: str) -> None:
        """Ввод описания"""
        self.DESCRIPTION_INPUT.fill(description)

    @allure.step("Открытие календаря")
    def open_date_picker(self) -> None:
        """Открытие календаря для выбора даты"""
        self.DATE_PICKER_BUTTON.click()

    @allure.step("Клик по кнопке Add")
    def click_add(self) -> None:
        """Нажатие кнопки добавления расхода"""
        self.ADD_BUTTON.click()

    @allure.step("Клик по кнопке Cancel")
    def click_cancel(self) -> None:
        """Нажатие кнопки отмены"""
        self.CANCEL_BUTTON.click()

    def get_amount_value(self) -> str:
        """Получение текущего значения поля Amount"""
        return self.AMOUNT_INPUT.input_value()

    def get_date_value(self) -> str:
        """Получение текущего значения поля Date"""
        return self.DATE_INPUT.input_value()

    def get_description_placeholder(self) -> str | None:
        """Получение placeholder описания"""
        return self.DESCRIPTION_INPUT.get_attribute("placeholder")

    def is_calendar_visible(self) -> bool:
        """Проверка видимости календаря"""
        return self.CALENDAR.is_visible()

    def is_amount_error_visible(self) -> bool:
        """Проверка видимости ошибки валидации суммы"""
        return self.AMOUNT_ERROR.is_visible()

    def is_category_error_visible(self) -> bool:
        """Проверка видимости ошибки валидации категории"""
        return self.CATEGORY_ERROR.is_visible()

    def is_currency_dropdown_open(self) -> bool:
        """Проверка что dropdown валют открыт"""
        return self.CURRENCY_RUB.is_visible()

    def is_category_input_disabled(self) -> bool:
        """Проверка что поле ввода категории заблокировано"""
        category_input = self.page.locator('input[placeholder="Add new category"]')
        return category_input.is_disabled(timeout=3000)
