from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.spending_page import SpendingPage
from mimesis import Person
from config import Config
import pytest
import allure
import json
import sys
import os


# ===============================
# HOOKS AND CONFIGURATION
# ===============================


def pytest_addoption(parser):
    """Добавление опций командной строки"""
    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environment: local, docker, staging",
    )


def pytest_configure(config):
    """Настройка категорий ошибок для Allure"""
    categories = [
        {
            "name": "UI Element Not Found",
            "messageRegex": ".*locator.*|.*element.*not.*found.*",
            "traceRegex": ".*playwright.*",
        },
        {
            "name": "Page Load Timeout",
            "messageRegex": ".*timeout.*|.*page.*load.*",
            "traceRegex": ".*playwright.*",
        },
        {
            "name": "Authentication Failed",
            "messageRegex": ".*login.*failed.*|.*auth.*error.*",
            "traceRegex": ".*",
        },
    ]

    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/categories.json", "w") as f:
        json.dump(categories, f, indent=2)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Автоматические скриншоты при падении тестов"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "page" in item.fixturenames:
            page = item.funcargs["page"]
            screenshot_bytes = page.screenshot()
            allure.attach(
                screenshot_bytes,
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )


# =============================
# ENVIRONMENT AND BROWSER SETUP
# =============================


@pytest.fixture(scope="session")
def environment(request):
    """Получение конфигурации окружения"""
    env_name = request.config.getoption("--env")
    return Config.get_env_config(env_name)


@pytest.fixture(scope="function")
def context(browser):
    """Браузер контекст с фиксированным размером окна"""
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    yield context
    context.close()


# =================
# ALLURE REPORTING
# =================


@pytest.fixture(scope="session", autouse=True)
def allure_environment(environment):
    """Настройка информации об окружении для Allure"""
    properties = [
        f"Environment={environment['frontend_url']}",
        f"Auth_URL={environment['auth_url']}",
        f"Python_Version={sys.version.split()[0]}",
        "Browser=Chromium",
        "Framework=Playwright + pytest",
    ]

    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/environment.properties", "w") as f:
        for prop in properties:
            f.write(f"{prop}\n")


# ==============
# PAGE FIXTURES
# ==============


@pytest.fixture
def login_page(page):
    """Фикстура для страницы авторизации"""
    return LoginPage(page)


@pytest.fixture
def main_page(page):
    """Фикстура для главной страницы"""
    return MainPage(page)


@pytest.fixture
def spending_page(page):
    """Фикстура для страницы расходов"""
    return SpendingPage(page)


# ===================
# USER DATA FIXTURES
# ===================


@pytest.fixture
def user_data():
    """Генерация случайных данных пользователя для каждого теста"""
    person = Person()
    username = person.username() + str(person.identifier(mask="###"))
    password = person.password(length=10)
    return username, password


@pytest.fixture
def registered_user(login_page, user_data):
    """Регистрация нового пользователя и возврат его данных"""
    username, password = user_data

    # Идем на страницу регистрации и заполняем форму
    login_page.open()
    login_page.click_create_account_button()

    login_page.page.fill('input[name="username"]', username)
    login_page.page.fill('input[name="password"]', password)
    login_page.page.fill('input[name="passwordSubmit"]', password)
    login_page.page.click('button:has-text("Sign Up")')

    return username, password


@pytest.fixture
def logged_in_user(login_page, registered_user):
    """Авторизация пользователя и переход на главную страницу"""
    username, password = registered_user

    # Входим в систему с зарегистрированными данными
    login_page.open()
    login_page.enter_username(username)
    login_page.enter_password(password)
    login_page.click_login_button()

    # Ждем пока нас перебросит на главную страницу
    login_page.page.wait_for_url("**/main", timeout=5000)

    return username, password
