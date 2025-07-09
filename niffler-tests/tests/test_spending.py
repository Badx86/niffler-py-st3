import allure
import random


@allure.feature("Добавление расходов/трат")
class TestSpending:
    """Тесты для страницы добавления трат"""

    @allure.story("Проверка элементов страницы")
    def test_spending_page_elements(self, spending_page, logged_in_user):
        """Проверяем что все элементы формы видимы и доступны"""
        spending_page.open()

        with allure.step("Проверка что находимся на странице добавления трат"):
            assert (
                spending_page.is_loaded()
            ), f"Не на странице трат. URL: {spending_page.page.url}"

        with allure.step("Проверка основных элементов формы"):
            assert spending_page.PAGE_TITLE.is_visible(), "Заголовок не виден"
            assert spending_page.AMOUNT_INPUT.is_visible(), "Поле Amount не видно"
            assert (
                spending_page.CURRENCY_DROPDOWN.is_visible()
            ), "Dropdown Currency не виден"
            assert spending_page.CATEGORY_INPUT.is_visible(), "Поле Category не видно"
            assert spending_page.DATE_INPUT.is_visible(), "Поле Date не видно"
            assert (
                spending_page.DESCRIPTION_INPUT.is_visible()
            ), "Поле Description не видно"

        with allure.step("Проверка кнопок"):
            assert spending_page.CANCEL_BUTTON.is_visible(), "Кнопка Cancel не видна"
            assert spending_page.ADD_BUTTON.is_visible(), "Кнопка Add не видна"

    @allure.story("Проверка dropdown валют")
    def test_currency_dropdown(self, spending_page, logged_in_user):
        """Проверяем что dropdown валют работает и содержит все валюты"""
        spending_page.open()

        with allure.step("Открытие dropdown валют"):
            spending_page.CURRENCY_DROPDOWN.click()

        with allure.step("Проверка наличия всех валют"):
            assert spending_page.CURRENCY_RUB.is_visible(), "Валюта RUB не видна"
            assert spending_page.CURRENCY_KZT.is_visible(), "Валюта KZT не видна"
            assert spending_page.CURRENCY_EUR.is_visible(), "Валюта EUR не видна"
            assert spending_page.CURRENCY_USD.is_visible(), "Валюта USD не видна"

        with allure.step("Выбор случайной валюты"):
            currencies = ["RUB", "KZT", "EUR", "USD"]
            selected_currency = random.choice(currencies)
            currency_locator = getattr(spending_page, f"CURRENCY_{selected_currency}")

            with allure.step(f"Выбрана валюта: {selected_currency}"):
                currency_locator.click()

    @allure.story("Проверка календаря")
    def test_date_picker(self, spending_page, logged_in_user):
        """Проверяем что календарь открывается и работает"""
        spending_page.open()

        with allure.step("Открытие календаря"):
            spending_page.open_date_picker()

        with allure.step("Проверка что календарь отображается"):
            assert spending_page.is_calendar_visible(), "Календарь не открылся"
            calendar_month = spending_page.get_calendar_month_locator()
            assert (
                calendar_month.is_visible()
            ), f"Заголовок месяца {spending_page.get_current_month_year()} не виден"

    @allure.story("Проверка значений по умолчанию")
    def test_default_values(self, spending_page, logged_in_user):
        """Проверяем дефолтные значения полей формы"""
        spending_page.open()

        with allure.step("Проверка дефолтных значений"):
            assert spending_page.get_amount_value() == "0", "Дефолтная сумма не равна 0"

            expected_date = spending_page.get_current_date_formatted()
            actual_date = spending_page.get_date_value()
            assert (
                actual_date == expected_date
            ), f"Дефолтная дата неверная. Ожидали: {expected_date}, получили: {actual_date}"

            assert (
                spending_page.get_description_placeholder() == "Type something"
            ), "Неверный placeholder"

    @allure.story("Создание валидной траты")
    def test_valid_spending_creation(self, spending_page, logged_in_user):
        """Проверяем создание траты с валидными данными"""
        spending_page.open()

        with allure.step("Заполнение всех полей"):
            spending_page.fill_amount(1500)

            # Случайный выбор валюты
            currencies = ["RUB", "KZT", "EUR", "USD"]
            random_currency = random.choice(currencies)
            spending_page.select_currency(random_currency)

            spending_page.fill_category("Food")
            spending_page.fill_description("Lunch at restaurant")

        with allure.step("Сохранение траты"):
            spending_page.click_add_button()

        with allure.step("Проверка возврата на главную страницу"):
            spending_page.page.wait_for_url("**/main", timeout=5000)
            assert "/main" in spending_page.page.url, "Не вернулись на главную страницу"

    @allure.story("Кнопка отмены")
    def test_cancel_button(self, spending_page, logged_in_user):
        """Проверяем что кнопка Cancel возвращает на главную"""
        spending_page.open()

        with allure.step("Частичное заполнение формы"):
            spending_page.fill_amount(500)
            spending_page.fill_category("Test")

        with allure.step("Нажатие кнопки Cancel"):
            spending_page.click_cancel_button()

        with allure.step("Проверка возврата на главную"):
            spending_page.page.wait_for_url("**/main", timeout=5000)
            assert (
                "/main" in spending_page.page.url
            ), "Cancel не вернул на главную страницу"

    @allure.story("Валидация обязательных полей")
    def test_required_fields(self, spending_page, logged_in_user):
        """Проверяем валидацию при незаполненных обязательных полях"""
        spending_page.open()

        with allure.step(
            "Попытка сохранения с дефолтными значениями (amount=0, пустая category)"
        ):
            spending_page.click_add_button()

        with allure.step("Проверка что остались на странице трат"):
            assert spending_page.is_loaded(), "Форма пропустила валидацию пустых полей"

        with allure.step("Проверка сообщений об ошибках"):
            assert (
                spending_page.AMOUNT_ERROR.is_visible()
            ), "Нет ошибки валидации для Amount"
            assert (
                spending_page.CATEGORY_ERROR.is_visible()
            ), "Нет ошибки валидации для Category"

        with allure.step("Исправление ошибки Amount"):
            spending_page.fill_amount(100)
            spending_page.click_add_button()

        with allure.step("Проверка что ошибка Amount исчезла, но Category осталась"):
            assert (
                not spending_page.AMOUNT_ERROR.is_visible()
            ), "Ошибка Amount не исчезла после исправления"
            assert (
                spending_page.CATEGORY_ERROR.is_visible()
            ), "Ошибка Category должна остаться"

        with allure.step("Исправление ошибки Category"):
            spending_page.fill_category("Test Category")
            spending_page.click_add_button()

        with allure.step("Проверка успешного сохранения"):
            spending_page.page.wait_for_url("**/main", timeout=5000)
            assert (
                "/main" in spending_page.page.url
            ), "Не перешли на главную после исправления всех ошибок"

    @allure.story("Валидация суммы")
    def test_amount_validation(self, spending_page, logged_in_user):
        """Проверяем валидацию поля Amount"""
        spending_page.open()

        with allure.step("Ввод различных значений суммы"):
            spending_page.fill_amount(0)
            assert spending_page.get_amount_value() == "0", "Не принимает значение 0"

            spending_page.fill_amount(999.99)
            assert (
                "999.99" in spending_page.get_amount_value()
            ), "Не принимает дробные числа"

            spending_page.fill_amount(1000000)
            assert (
                "1000000" in spending_page.get_amount_value()
            ), "Не принимает большие числа"

    @allure.story("Ввод категории")
    def test_category_input(self, spending_page, logged_in_user):
        """Проверяем ввод новой категории"""
        spending_page.open()

        with allure.step("Ввод различных категорий"):
            test_categories = ["Food", "Transport", "Entertainment", "Shopping"]

            for category in test_categories:
                spending_page.fill_category(category)
                assert (
                    spending_page.CATEGORY_INPUT.input_value() == category
                ), f"Категория {category} не сохранилась"

    @allure.story("Навигация на страницу трат")
    def test_navigation_to_spending(self, main_page, spending_page, logged_in_user):
        """Проверяем переход на страницу трат с главной страницы"""

        with allure.step("Проверка что находимся на главной странице"):
            assert main_page.is_loaded(), "Не на главной странице"

        with allure.step("Клик по кнопке New spending"):
            main_page.NEW_SPENDING_BUTTON.click()

        with allure.step("Проверка перехода на страницу трат"):
            main_page.page.wait_for_url("**/spending", timeout=5000)
            assert spending_page.is_loaded(), "Не перешли на страницу добавления трат"
