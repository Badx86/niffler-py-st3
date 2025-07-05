import allure
from abc import ABC, abstractmethod


class BasePage(ABC):
    """
    Базовая страница для всех остальных страниц
    """

    def __init__(self, page):
        self.page = page

    @allure.step("Переход по URL: {url}")
    def navigate_to(self, url):
        """
        Переходим на нужную страницу и ждем пока она полностью загрузится
        networkidle опция, используемая для определения момента, когда страница считается загруженной
        """
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')

    @abstractmethod
    def is_loaded(self):
        """
        Каждая страница должна уметь проверять, что она загрузилась
        """
        pass
