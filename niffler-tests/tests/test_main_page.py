import allure
from pages.main_page import MainPage
from components.header import HeaderComponent
from components.filters.time_filter import TimeFilterComponent
from components.filters.currency_filter import CurrencyFilterComponent
from actions.profile_actions import ProfileActions
from playwright.sync_api import expect


@allure.feature("Главная страница")
class TestMainPage:
    """Тесты для проверки главной страницы приложения"""

    @allure.story("Проверка основных элементов")
    def test_main_page_elements(self, main_page, logged_in_user):
        """Проверяем что на главной странице есть все основные элементы"""
        header = HeaderComponent(main_page.page)

        with allure.step("Проверка что находимся на главной странице"):
            header.LOGO.wait_for(state="visible")
            assert (
                main_page.is_loaded()
            ), f"Не на главной странице. URL: {main_page.page.url}"

        with allure.step("Проверка основных элементов"):
            assert header.is_logo_visible(), "Логотип Niffler не видим"
            assert (
                header.is_new_spending_button_visible()
            ), "Кнопка New spending не видима"
            assert header.is_profile_button_visible(), "Кнопка профиля не видима"

        with allure.step("Проверка заголовков разделов"):
            statistics_title = main_page.page.locator('h2:has-text("Statistics")')
            history_title = main_page.page.locator(
                'h2:has-text("History of Spendings")'
            )
            assert statistics_title.is_visible(), "Заголовок Statistics не виден"
            assert history_title.is_visible(), "Заголовок History of Spendings не виден"

    @allure.story("Проверка элемента поиска")
    def test_search_functionality(self, main_page, logged_in_user):
        """Проверяем что поиск трат работает правильно"""

        with allure.step("Проверка поля поиска"):
            search_input = main_page.page.locator('input[placeholder="Search"]')
            assert (
                search_input.get_attribute("placeholder") == "Search"
            ), "Неверный placeholder в поле поиска"

        with allure.step("Проверка кнопки поиска"):
            search_button = main_page.page.locator('button[aria-label="search"]')
            assert search_button.is_visible(), "Кнопка поиска не видима"

    @allure.story("Проверка фильтра времени")
    def test_time_filter_dropdown(self, main_page, logged_in_user):
        """Проверяем что фильтр по времени работает и показывает все варианты"""
        time_filter = TimeFilterComponent(main_page.page)

        with allure.step("Клик по фильтру времени"):
            time_filter.open_filter()

        with allure.step("Проверка наличия всех опций фильтра времени"):
            assert time_filter.are_all_options_visible(), "Не все опции времени видны"

    @allure.story("Проверка фильтра валют")
    def test_currency_filter_dropdown(self, main_page, logged_in_user):
        """Проверяем что фильтр по валютам работает и показывает все валюты"""
        currency_filter = CurrencyFilterComponent(main_page.page)

        with allure.step("Клик по фильтру валют"):
            currency_filter.open_filter()

        with allure.step("Проверка наличия всех опций фильтра валют"):
            assert currency_filter.are_all_options_visible(), "Не все опции валют видны"

    @allure.story("Проверка меню профиля")
    def test_profile_menu(self, main_page, logged_in_user):
        """Проверяем что меню профиля открывается и показывает все пункты"""
        profile_actions = ProfileActions(main_page)

        with allure.step("Клик по кнопке профиля"):
            menu_visible = profile_actions.open_profile_menu()
            assert menu_visible, "Меню профиля не открылось"

    @allure.story("Проверка дефолтного (без трат) состояния")
    def test_empty_state(self, main_page, logged_in_user):
        """Проверяем что новому пользователю показывается правильное сообщение"""

        with allure.step("Проверка сообщения об отсутствии трат"):
            # Улучшенная стратегия ожидания - ждем загрузки страницы, потом элемент
            main_page.page.wait_for_load_state("networkidle")
            no_spendings = main_page.page.locator('text="There are no spendings"')
            # Используем expect с таймаутом для более надежного ожидания
            expect(no_spendings).to_be_visible(timeout=10000)

        with allure.step("Проверка изображения Niffler"):
            # Аналогично для картинки
            niffler_image = main_page.page.locator('img[alt="Lonely niffler"]')
            expect(niffler_image).to_be_visible(timeout=5000)

    @allure.story("Проверка состояния кнопки Delete")
    def test_delete_button_state(self, main_page, logged_in_user):
        """Проверяем что кнопка удаления неактивна когда нет трат"""

        with allure.step("Проверка кнопки Delete"):
            delete_btn = main_page.page.locator('button[id="delete"]')
            assert (
                delete_btn.is_disabled()
            ), "Кнопка Delete должна быть неактивной для пользователя без трат"
