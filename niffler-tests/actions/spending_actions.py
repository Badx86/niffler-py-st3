import allure
from pages.spending_page import SpendingPage
from components.forms.spending_form import SpendingFormComponent
from components.header import HeaderComponent


class SpendingActions:
    """Действия для работы с тратами - создание, редактирование, удаление"""

    def __init__(self, page):
        self.page = page
        self.spending_page = SpendingPage(page)
        self.spending_form = SpendingFormComponent(page)
        self.header = HeaderComponent(page)

    @allure.step("Создание траты")
    def create_spending(self, amount, currency, category, description=""):
        """
        Создание новой траты с заданными параметрами

        Args:
            amount: сумма траты
            currency: валюта (RUB, USD, EUR, KZT)
            category: категория траты
            description: описание (опционально)

        Returns:
            bool: успешность создания
        """
        self.spending_page.open()

        # Заполняем все поля
        self.spending_form.fill_amount(amount)
        self.spending_form.select_currency(currency)
        self.spending_form.fill_category(category)

        if description:
            self.spending_form.fill_description(description)

        # Сохраняем трату
        self.spending_form.click_add()
        self.page.wait_for_url("**/main", timeout=5000)

        return "/main" in self.page.url

    @allure.step("Переход к созданию траты через кнопку")
    def navigate_to_spending_from_main(self):
        """
        Переход к созданию траты с главной страницы через кнопку

        Returns:
            bool: находимся ли на странице создания трат
        """
        self.header.click_new_spending()
        self.page.wait_for_url("**/spending", timeout=5000)

        return self.spending_page.is_loaded()

    @allure.step("Отмена создания траты")
    def cancel_spending_creation(self):
        """
        Частичное заполнение формы и отмена создания

        Returns:
            bool: вернулись ли на главную страницу
        """
        self.spending_page.open()

        # Частичное заполнение формы
        self.spending_form.fill_amount(500)
        self.spending_form.fill_category("Test")

        # Нажатие кнопки Cancel
        self.spending_form.click_cancel()

        self.page.wait_for_url("**/main", timeout=5000)
        return "/main" in self.page.url

    @allure.step("Попытка создания траты с невалидными данными")
    def try_create_invalid_spending(self):
        """
        Попытка сохранения с дефолтными значениями (amount=0, пустая category)

        Returns:
            bool: отображаются ли ошибки валидации
        """
        self.spending_page.open()
        self.spending_form.click_add()

        return (self.spending_form.is_amount_error_visible() and
                self.spending_form.is_category_error_visible())

    @allure.step("Исправление ошибок валидации")
    def fix_validation_errors(self):
        """
        Пошаговое исправление ошибок валидации

        Returns:
            bool: успешность исправления всех ошибок
        """
        # Исправление ошибки Amount
        self.spending_form.fill_amount(100)
        self.spending_form.click_add()

        amount_error_gone = not self.spending_form.is_amount_error_visible()
        category_error_remains = self.spending_form.is_category_error_visible()

        # Исправление ошибки Category
        self.spending_form.fill_category("Test Category")
        self.spending_form.click_add()

        self.page.wait_for_url("**/main", timeout=5000)
        success = "/main" in self.page.url

        return amount_error_gone and category_error_remains and success
