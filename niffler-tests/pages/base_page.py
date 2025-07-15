from abc import ABC, abstractmethod
from playwright.sync_api import Page
from typing import Any
import allure


class BasePage(ABC):
    """
    Базовая страница для всех остальных страниц
    """

    def __init__(self, page: Page, environment: dict[str, Any] = None) -> None:
        self.page = page
        self.environment = environment or {}

    @allure.step("Переход по URL: {url}")
    def navigate_to(self, url: str) -> None:
        """
        Переходим на нужную страницу и ждем пока она полностью загрузится
        networkidle опция, используемая для определения момента, когда страница считается загруженной
        """
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def get_full_url(self, base_key: str, endpoint: str = "") -> str:
        """
        Получение полного URL из конфигурации окружения

        Args:
            base_key: ключ базового URL ('auth_url' или 'frontend_url')
            endpoint: эндпоинт для добавления к базовому URL
        """
        base_url = self.environment.get(base_key, "")

        # Если base_url пустой, возвращаем fallback URL
        if not base_url:
            if base_key == "auth_url":
                base_url = "http://auth.niffler.dc:9000"
            elif base_key == "frontend_url":
                base_url = "http://frontend.niffler.dc"
            else:
                base_url = "http://localhost:3000"  # дефолт

        return f"{base_url}{endpoint}"

    @abstractmethod
    def is_loaded(self) -> bool:
        """
        Каждая страница должна уметь проверять, что она загрузилась
        """
        pass
