import allure
import random
from actions.spending_actions import SpendingActions
from builders.spending_builder import SpendingBuilder
from components.forms.spending_form import SpendingFormComponent
from pages.main_page import MainPage
from pages.spending_page import SpendingPage


@allure.feature("Добавление расходов/трат")
class TestSpending:
    """Тесты для страницы добавления трат"""

    @allure.story("Проверка элементов страницы")
    def test_spending_page_elements(self, authenticated_page):
        """Проверяем что все элементы формы видимы и доступны"""
        spending_page = SpendingPage(authenticated_page)
        spending_form = SpendingFormComponent(authenticated_page)

        spending_page.open()

        with allure.step("Проверка что находимся на странице добавления трат"):
            assert spending_page.is_loaded(), f"Не на странице трат. URL: {authenticated_page.url}"

        with allure.step("Проверка основных элементов формы"):
            assert spending_form.PAGE_TITLE.is_visible(), "Заголовок не виден"
            assert spending_form.AMOUNT_INPUT.is_visible(), "Поле Amount не видно"
            assert spending_form.CURRENCY_DROPDOWN.is_visible(), "Dropdown Currency не виден"
            assert spending_form.CATEGORY_INPUT.is_visible(), "Поле Category не видно"
            assert spending_form.DATE_INPUT.is_visible(), "Поле Date не видно"
            assert spending_form.DESCRIPTION_INPUT.is_visible(), "Поле Description не видно"

        with allure.step("Проверка кнопок"):
            assert spending_form.CANCEL_BUTTON.is_visible(), "Кнопка Cancel не видна"
            assert spending_form.ADD_BUTTON.is_visible(), "Кнопка Add не видна"

    @allure.story("Проверка dropdown валют")
    def test_currency_dropdown(self, authenticated_page):
        """Проверяем что dropdown валют работает и содержит все валюты"""
        spending_page = SpendingPage(authenticated_page)
        spending_form = SpendingFormComponent(authenticated_page)

        spending_page.open()

        with allure.step("Открытие dropdown валют"):
            spending_form.CURRENCY_DROPDOWN.click()

        with allure.step("Проверка наличия всех валют"):
            assert spending_form.CURRENCY_RUB.is_visible(), "Валюта RUB не видна"
            assert spending_form.CURRENCY_KZT.is_visible(), "Валюта KZT не видна"
            assert spending_form.CURRENCY_EUR.is_visible(), "Валюта EUR не видна"
            assert spending_form.CURRENCY_USD.is_visible(), "Валюта USD не видна"

        with allure.step("Выбор случайной валюты"):
            currencies = ["RUB", "KZT", "EUR", "USD"]
            selected_currency = random.choice(currencies)
            currency_locator = getattr(spending_form, f"CURRENCY_{selected_currency}")

            with allure.step(f"Выбрана валюта: {selected_currency}"):
                currency_locator.click()

    @allure.story("Проверка календаря")
    def test_date_picker(self, authenticated_page):
        """Проверяем что календарь открывается и работает"""
        spending_page = SpendingPage(authenticated_page)
        spending_form = SpendingFormComponent(authenticated_page)

        spending_page.open()

        with allure.step("Открытие календаря"):
            spending_form.open_date_picker()

        with allure.step("Проверка что календарь отображается"):
            assert spending_form.is_calendar_visible(), "Календарь не открылся"

            calendar_month = spending_form.get_calendar_month_locator()
            assert calendar_month.is_visible(), f"Заголовок месяца {spending_form.get_current_month_year()} не виден"

    @allure.story("Проверка значений по умолчанию")
    def test_default_values(self, authenticated_page):
        """Проверяем дефолтные значения полей формы"""
        spending_page = SpendingPage(authenticated_page)
        spending_form = SpendingFormComponent(authenticated_page)

        spending_page.open()

        with allure.step("Проверка дефолтных значений"):
            assert spending_form.get_amount_value() == "0", "Дефолтная сумма не равна 0"

            expected_date = spending_form.get_current_date_formatted()
            actual_date = spending_form.get_date_value()

            assert actual_date == expected_date, (f"Дефолтная дата неверная. "
                                                  f"Ожидали: {expected_date}, получили: {actual_date}")
            assert spending_form.get_description_placeholder() == "Type something", "Неверный placeholder"

    @allure.story("Создание валидной траты")
    def test_valid_spending_creation(self, authenticated_page, spend_db, logged_in_user):
        """Проверяем создание траты с валидными данными"""
        spending_page = SpendingPage(authenticated_page)
        spending_actions = SpendingActions(spending_page)
        spending_data = (
            SpendingBuilder()
            .with_random_amount(1000, 2000)
            .with_random_currency()
            .with_random_category()
            .with_random_description()
            .build()
        )

        success = spending_actions.create_spending(
            spending_data.amount,
            spending_data.currency,
            spending_data.category,
            spending_data.description,
        )
        assert success, "Не удалось создать трату"

        with allure.step("БД проверка - данные сохранились"):
            from sqlmodel import Session, select
            from models.data_models import Spend, Category

            with Session(spend_db.engine) as session:
                # JOIN проверяет что найденная трата действительно привязана к той категории, что мы создали через UI
                statement = (
                    select(Spend)
                    .join(Category, Spend.category_id == Category.id)  # type: ignore
                    .where(
                        Spend.amount == spending_data.amount,
                        Spend.description == spending_data.description,
                        Category.name == spending_data.category
                    )
                )

                found_spends = session.exec(statement).all()
                assert len(found_spends) > 0, f"Трата с категорией '{spending_data.category}' не найдена в БД"

                test_spend = found_spends[-1]
                assert test_spend.amount == spending_data.amount
                assert test_spend.description == spending_data.description

    @allure.story("Кнопка отмены")
    def test_cancel_button(self, authenticated_page):
        """Проверяем что кнопка Cancel возвращает на главную"""
        spending_page = SpendingPage(authenticated_page)
        spending_actions = SpendingActions(spending_page)

        success = spending_actions.cancel_spending_creation()
        assert success, "Cancel не вернул на главную страницу"

    @allure.story("Валидация обязательных полей")
    def test_required_fields(self, authenticated_page, spend_db, logged_in_user):
        """Проверяем валидацию при незаполненных обязательных полях"""
        spending_page = SpendingPage(authenticated_page)
        spending_actions = SpendingActions(spending_page)

        with allure.step("Запоминаем начальное состояние БД"):
            initial_count = len(spend_db.get_user_spends(logged_in_user.username))

        with allure.step("Попытка сохранения с дефолтными значениями (amount=0, пустая category)"):
            errors_shown = spending_actions.try_create_invalid_spending()
            assert errors_shown, "Форма пропустила валидацию пустых полей"

        with allure.step("БД проверка - невалидные данные не сохранились"):
            current_count = len(spend_db.get_user_spends(logged_in_user.username))
            assert current_count == initial_count, "Невалидные данные попали в БД!"

        with allure.step("Исправление ошибок"):
            success = spending_actions.fix_validation_errors()
            assert success, "Не удалось исправить ошибки валидации"

    @allure.story("Валидация суммы")
    def test_amount_validation(self, authenticated_page):
        """Проверяем валидацию поля Amount"""
        spending_page = SpendingPage(authenticated_page)
        spending_form = SpendingFormComponent(authenticated_page)

        spending_page.open()

        with allure.step("Ввод различных значений суммы"):
            spending_form.fill_amount(0)
            assert spending_form.get_amount_value() == "0", "Не принимает значение 0"

            spending_form.fill_amount(999.99)
            assert "999.99" in spending_form.get_amount_value(), "Не принимает дробные числа"

            spending_form.fill_amount(1000000)
            assert "1000000" in spending_form.get_amount_value(), "Не принимает большие числа"

    @allure.story("Ввод категории")
    def test_category_input(self, authenticated_page, spends_client):
        """Проверяем ввод новой категории"""
        spending_page = SpendingPage(authenticated_page)
        spending_form = SpendingFormComponent(authenticated_page)

        spending_page.open()

        with allure.step("Ввод различных категорий"):
            test_categories = ["Food", "Transport", "Entertainment", "Shopping"]

            for category in test_categories:
                spending_form.fill_category(category)
                assert spending_form.CATEGORY_INPUT.input_value() == category, f"Категория {category} не сохранилась"

        with allure.step("Очистка тестовых категорий"):
            try:
                categories = spends_client.get_categories()
                test_category_ids = [c.id for c in categories if c.category in test_categories]
                if test_category_ids:
                    spends_client.remove_categories(test_category_ids)
            except Exception as e:
                allure.attach(f"Ошибка очистки: {str(e)}", name="Cleanup error")

    @allure.story("Навигация на страницу трат")
    def test_navigation_to_spending(self, authenticated_page):
        """Проверяем переход на страницу трат с главной страницы"""
        main_page = MainPage(authenticated_page)
        spending_actions = SpendingActions(main_page)

        with allure.step("Проверка что находимся на главной странице"):
            assert main_page.is_loaded(), "Не на главной странице"

        with allure.step("Клик по кнопке New spending"):
            success = spending_actions.navigate_to_spending_from_main()
            assert success, "Не перешли на страницу добавления трат"
