import allure
from pages.main_page import MainPage


@allure.feature("Главная страница")
class TestMainPage:

    @allure.story("Проверка основных элементов")
    def test_main_page_elements(self, page, logged_in_user):
        """Тест проверки основных элементов главной страницы"""
        main_page = MainPage(page)

        with allure.step("Проверка что находимся на главной странице"):
            assert main_page.is_on_main_page(), f"Не на главной странице. URL: {page.url}"

        with allure.step("Проверка основных элементов"):
            assert page.locator(main_page.LOGO).is_visible(), "Логотип Niffler не видим"
            assert page.locator(main_page.NEW_SPENDING_BUTTON).is_visible(), "Кнопка New spending не видима"
            assert page.locator(main_page.PROFILE_BUTTON).is_visible(), "Кнопка профиля не видима"

        with allure.step("Проверка заголовков разделов"):
            assert page.locator(main_page.STATISTICS_TITLE).is_visible(), "Заголовок Statistics не виден"
            assert page.locator(main_page.HISTORY_TITLE).is_visible(), "Заголовок History of Spendings не виден"

    @allure.story("Проверка элемента поиска")
    def test_search_functionality(self, page, logged_in_user):
        """Тест проверки поля поиска и кнопки поиска"""
        main_page = MainPage(page)

        with allure.step("Проверка поля поиска"):
            search_input = page.locator(main_page.SEARCH_INPUT)
            assert search_input.get_attribute('placeholder') == "Search", "Неверный placeholder в поле поиска"

        with allure.step("Проверка кнопки поиска"):
            assert page.locator(main_page.SEARCH_BUTTON).is_visible(), "Кнопка поиска не видима"

    @allure.story("Проверка фильтра времени")
    def test_time_filter_dropdown(self, page, logged_in_user):
        """Тест проверки выпадающего списка фильтра времени"""
        main_page = MainPage(page)

        with allure.step("Клик по фильтру времени"):
            page.locator(main_page.TIME_FILTER_BUTTON).click()

        with allure.step("Проверка наличия всех опций фильтра времени"):
            assert page.locator(main_page.TIME_OPTION_ALL).is_visible(), "Опция 'All time' не видна"
            assert page.locator(main_page.TIME_OPTION_LAST_MONTH).is_visible(), "Опция 'Last month' не видна"
            assert page.locator(main_page.TIME_OPTION_LAST_WEEK).is_visible(), "Опция 'Last week' не видна"
            assert page.locator(main_page.TIME_OPTION_TODAY).is_visible(), "Опция 'Today' не видна"

    @allure.story("Проверка фильтра валют")
    def test_currency_filter_dropdown(self, page, logged_in_user):
        """Тест проверки выпадающего списка фильтра валют"""
        main_page = MainPage(page)

        with allure.step("Клик по фильтру валют"):
            page.locator(main_page.CURRENCY_FILTER_BUTTON).click()

        with allure.step("Проверка наличия всех опций фильтра валют"):
            assert page.locator(main_page.CURRENCY_OPTION_ALL).is_visible(), "Опция 'ALL' не видна"
            assert page.locator(main_page.CURRENCY_OPTION_RUB).is_visible(), "Опция 'RUB' не видна"
            assert page.locator(main_page.CURRENCY_OPTION_KZT).is_visible(), "Опция 'KZT' не видна"
            assert page.locator(main_page.CURRENCY_OPTION_EUR).is_visible(), "Опция 'EUR' не видна"
            assert page.locator(main_page.CURRENCY_OPTION_USD).is_visible(), "Опция 'USD' не видна"

    @allure.story("Проверка меню профиля")
    def test_profile_menu(self, page, logged_in_user):
        """Тест проверки меню профиля"""
        main_page = MainPage(page)

        with allure.step("Клик по кнопке профиля"):
            page.locator(main_page.PROFILE_BUTTON).click()

        with allure.step("Проверка наличия всех пунктов меню профиля"):
            assert page.locator(main_page.PROFILE_MENU_PROFILE).is_visible(), "Пункт 'Profile' не виден"
            assert page.locator(main_page.PROFILE_MENU_FRIENDS).is_visible(), "Пункт 'Friends' не виден"
            assert page.locator(main_page.PROFILE_MENU_ALL_PEOPLE).is_visible(), "Пункт 'All People' не виден"
            assert page.locator(main_page.PROFILE_MENU_SIGN_OUT).is_visible(), "Пункт 'Sign out' не виден"

    @allure.story("Проверка дефолтного (без трат) состояния")
    def test_empty_state(self, page, logged_in_user):
        """Тест проверки дефолтного состояния для нового пользователя"""
        main_page = MainPage(page)

        with allure.step("Проверка сообщения об отсутствии трат"):
            # Ждем загрузки сообщения
            page.wait_for_selector('text="There are no spendings"', timeout=5000)
            assert page.locator(
                main_page.NO_SPENDINGS_MESSAGE).is_visible(), "Сообщение 'There are no spendings' не видимо"

        with allure.step("Проверка изображения Niffler"):
            # Ждем загрузки изображения
            page.wait_for_selector('img[alt="Lonely niffler"]', timeout=5000)
            assert page.locator(main_page.NIFFLER_IMAGE).is_visible(), "Изображение Niffler не видимо"

    @allure.story("Проверка наличия кнопки Delete")
    def test_delete_button_state(self, page, logged_in_user):
        """Тест проверки состояния кнопки Delete"""
        main_page = MainPage(page)

        with allure.step("Проверка кнопки Delete"):
            delete_btn = page.locator(main_page.DELETE_BUTTON)
            assert delete_btn.is_disabled(), "Кнопка Delete должна быть неактивной для пользователя без трат"
