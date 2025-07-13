from .base_page import BasePage
from playwright.sync_api import Page
from typing import Dict, Any


class MainPage(BasePage):
    """Главная страница приложения после входа в систему"""

    def __init__(self, page: Page, environment: Dict[str, Any] = None) -> None:
        super().__init__(page, environment)

    def open(self) -> None:
        """Переход на главную страницу"""
        main_url = self.get_full_url("frontend_url", "/main")
        self.navigate_to(main_url)

    def is_loaded(self) -> bool:
        """
        Проверяем что мы действительно на главной странице
        Смотрим на URL и заголовок страницы
        """
        current_url = self.page.url
        title = self.page.title()

        # Получаем базовый URL из конфигурации для проверки
        frontend_base = self.environment.get("frontend_url", "")
        base_domain = frontend_base.replace("http://", "").replace("https://", "")

        is_correct_url = base_domain in current_url and "/main" in current_url
        is_correct_title = title == "Niffler"
        return is_correct_url and is_correct_title
