from abc import ABC, abstractmethod
from playwright.sync_api import Page
import allure


class BasePage(ABC):
    """
    Базовая страница для всех остальных страниц
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    @allure.step("Переход по URL: {url}")
    def navigate_to(self, url: str) -> None:
        """
        Переходим на нужную страницу и ждем пока она полностью загрузится
        networkidle опция, используемая для определения момента, когда страница считается загруженной
        """
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    @abstractmethod
    def is_loaded(self) -> bool:
        """
        Каждая страница должна уметь проверять, что она загрузилась
        """
        pass
