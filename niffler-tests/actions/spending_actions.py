import allure
from typing import Any
from pages.spending_page import SpendingPage
from components.forms.spending_form import SpendingFormComponent
from components.header import HeaderComponent
from exceptions import UIError, ValidationError


class SpendingActions:
    """Действия для работы с тратами - создание, редактирование, удаление"""

    def __init__(self, page_object: Any) -> None:
        self.page = page_object.page
        self.spending_page = SpendingPage(self.page)
        self.spending_form = SpendingFormComponent(self.page)
        self.header = HeaderComponent(self.page)

    @allure.step("Создание траты")
    def create_spending(
            self, amount: int | float, currency: str, category: str, description: str = ""
    ) -> bool:
        try:
            self.spending_page.open()

            # Проверяем лимит перед созданием
            if self.spending_form.is_category_input_disabled():
                raise ValidationError(
                    "Достигнут лимит категорий (8), нельзя создавать новые траты",
                    field="category",
                    value=category
                )

            # Заполняем поля
            self.spending_form.fill_amount(amount)
            self.spending_form.select_currency(currency)
            self.spending_form.fill_category(category)

            if description:
                self.spending_form.fill_description(description)

            # Сохраняем трату
            self.spending_form.click_add()
            self.page.wait_for_url("**/main", timeout=5000)

            if "/main" not in self.page.url:
                raise UIError(
                    "После сохранения не перешли на главную страницу",
                    page="spending",
                    action="create_spending"
                )

            return True

        except (ValidationError, UIError):
            # Пробрасываем ошибки
            raise
        except Exception as e:
            raise UIError(
                f"Неожиданная ошибка при создании траты: {str(e)}",
                page="spending",
                action=f"create_spending[{amount} {currency} {category}]"
            )

    @allure.step("Переход к созданию траты через кнопку")
    def navigate_to_spending_from_main(self) -> bool:
        """
        Переход к созданию траты с главной страницы через кнопку

        Returns:
            bool: находимся ли на странице создания трат
        """
        self.header.click_new_spending()
        self.page.wait_for_url("**/spending", timeout=5000)

        return self.spending_page.is_loaded()

    @allure.step("Отмена создания траты")
    def cancel_spending_creation(self) -> bool:
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
    def try_create_invalid_spending(self) -> bool:
        """
        Попытка сохранения с дефолтными значениями (amount=0, пустая category)

        Returns:
            bool: отображаются ли ошибки валидации
        """
        self.spending_page.open()
        self.spending_form.click_add()

        return (
            self.spending_form.is_amount_error_visible()
            and self.spending_form.is_category_error_visible()
        )

    @allure.step("Исправление ошибок валидации")
    def fix_validation_errors(self) -> bool:
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

    @allure.step("Проверка лимита ввода категорий")
    def check_category_input_limit(self) -> dict:
        """Проверка что поле ввода новых категорий заблокировано при лимите"""
        self.spending_page.open()

        return {
            "category_input_disabled": self.spending_form.is_category_input_disabled()
        }
