import allure


class BasePage:
    def __init__(self, page):
        self.page = page

    @allure.step("Переход по URL: {url}")
    def go_to(self, url):
        self.page.goto(url)

    @allure.step("Получение заголовка страницы")
    def get_title(self):
        return self.page.title()

    @allure.step("Поиск элемента по селектору: {selector}")
    def find_element(self, selector):
        """
        Найти элемент по селектору.
        :param selector: CSS-селектор для поиска элемента
        :return: Элемент (объект типа Locator)
        """
        return self.page.locator(selector)

    @allure.step("Поиск всех элементов по селектору: {selector}")
    def find_elements(self, selector):
        """
        Найти все элементы по селектору.
        :param selector: CSS-селектор для поиска элементов
        :return: Список элементов (объекты типа Locator)
        """
        return self.page.locator(selector).all()  # Заменил на locator
