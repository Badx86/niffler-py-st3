import allure


class TimeFilterComponent:
    """Компонент фильтра по времени для трат"""

    def __init__(self, page):
        self.page = page

        # Фильтр времени
        self.TIME_FILTER_BUTTON = self.page.locator('div[id="period"]')

        # Варианты в фильтре времени
        self.TIME_OPTION_ALL = self.page.locator('li[data-value="ALL"]')
        self.TIME_OPTION_LAST_MONTH = self.page.locator('li[data-value="MONTH"]')
        self.TIME_OPTION_LAST_WEEK = self.page.locator('li[data-value="WEEK"]')
        self.TIME_OPTION_TODAY = self.page.locator('li[data-value="TODAY"]')

    @allure.step("Открытие фильтра времени")
    def open_filter(self):
        """Открытие выпадающего списка фильтра времени"""
        self.TIME_FILTER_BUTTON.click()

    @allure.step("Выбор периода: {period}")
    def select_period(self, period):
        """Выбор конкретного периода времени"""
        self.open_filter()
        if period == "ALL":
            self.TIME_OPTION_ALL.click()
        elif period == "MONTH":
            self.TIME_OPTION_LAST_MONTH.click()
        elif period == "WEEK":
            self.TIME_OPTION_LAST_WEEK.click()
        elif period == "TODAY":
            self.TIME_OPTION_TODAY.click()

    def are_all_options_visible(self):
        """Проверка что все опции фильтра времени видны"""
        return (self.TIME_OPTION_ALL.is_visible() and
                self.TIME_OPTION_LAST_MONTH.is_visible() and
                self.TIME_OPTION_LAST_WEEK.is_visible() and
                self.TIME_OPTION_TODAY.is_visible())
