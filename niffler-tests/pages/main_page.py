from .base_page import BasePage
from playwright.sync_api import Page
from typing import Any


class MainPage(BasePage):
    """Главная страница приложения после входа в систему"""

    def __init__(self, page: Page, environment: dict[str, Any] = None) -> None:
        super().__init__(page, environment)

    def open(self) -> None:
        """Переход на главную страницу"""
        main_url = self.get_full_url("frontend_url", "/main")
        self.navigate_to(main_url)

    def is_loaded(self) -> bool:
        """Проверяем что мы действительно на главной странице"""
        current_url = self.page.url
        title = self.page.title()
        frontend_base = self.environment.get("frontend_url", "")
        base_domain = frontend_base.replace("http://", "").replace("https://", "")
        is_correct_url = base_domain in current_url and "/main" in current_url
        is_correct_title = title == "Niffler"
        return is_correct_url and is_correct_title

    def go_to_main(self) -> None:
        """Переход на главную страницу"""
        main_url = self.get_full_url("frontend_url", "/main")
        self.navigate_to(main_url)

    def find_spending_by_category(self, category: str) -> dict | None:
        """Найти трату по категории"""
        # Находим строку с категорией
        row = self.page.locator(f'tr:has(td:has-text("{category}"))')

        if row.count() == 0:
            return None

        cells = row.locator('td')

        return {
            "category": cells.nth(1).text_content().strip(),  # td[1] - Category
            "amount": cells.nth(2).text_content().strip(),  # td[2] - Amount
            "date": cells.nth(4).text_content().strip()  # td[4] - Date
        }
