from .base_page import BasePage


class MainPage(BasePage):
    """Главная страница приложения после входа в систему"""

    def __init__(self, page):
        super().__init__(page)

    def open(self):
        """Переход на главную страницу"""
        self.navigate_to("http://frontend.niffler.dc/main")

    def is_loaded(self):
        """
        Проверяем что мы действительно на главной странице
        Смотрим на URL и заголовок страницы
        """
        current_url = self.page.url
        title = self.page.title()
        is_correct_url = "frontend.niffler.dc" in current_url and "/main" in current_url
        is_correct_title = title == "Niffler"
        return is_correct_url and is_correct_title
