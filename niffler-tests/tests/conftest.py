from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from mimesis import Person
from config import Config
import pytest
import allure
import json
import sys
import os


# Добавить опции
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="local",
                     help="Environment: local, docker, staging")


# Окружение
@pytest.fixture(scope="session")
def environment(request):
    env_name = request.config.getoption("--env")
    return Config.get_env_config(env_name)


# Allure окружение
@pytest.fixture(scope="session", autouse=True)
def allure_environment(environment):
    properties = [
        f"Environment={environment['frontend_url']}",
        f"Auth_URL={environment['auth_url']}",
        f"Python_Version={sys.version.split()[0]}",
        f"Browser=Chromium",
        f"Framework=Playwright + pytest"
    ]

    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/environment.properties", "w") as f:
        for prop in properties:
            f.write(f"{prop}\n")


# Категории ошибок
def pytest_configure(config):
    categories = [
        {
            "name": "UI Element Not Found",
            "messageRegex": ".*locator.*|.*element.*not.*found.*",
            "traceRegex": ".*playwright.*"
        },
        {
            "name": "Page Load Timeout",
            "messageRegex": ".*timeout.*|.*page.*load.*",
            "traceRegex": ".*playwright.*"
        },
        {
            "name": "Authentication Failed",
            "messageRegex": ".*login.*failed.*|.*auth.*error.*",
            "traceRegex": ".*"
        }
    ]

    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/categories.json", "w") as f:
        json.dump(categories, f, indent=2)


@pytest.fixture(scope="session")
def playwright():
    """Создаем экземпляр Playwright для всей сессии тестов"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright):
    """Создаем браузер для каждого теста отдельно"""
    print('\nstart browser...')
    browser = playwright.chromium.launch(headless=False)  # headless=False чтобы видеть что происходит
    yield browser
    print('\nquit browser...')
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    """Создаем контекст браузера (как отдельное окно)"""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Создаем страницу (вкладку) для теста"""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def user_data():
    """Генерируем случайные данные пользователя для каждого теста"""
    person = Person()
    username = person.username() + str(person.identifier(mask='###'))
    password = person.password(length=10)
    return username, password


@pytest.fixture
def registered_user(page, user_data):
    """Регистрируем нового пользователя и возвращаем его данные"""
    username, password = user_data
    login_page = LoginPage(page)

    # Идем на страницу регистрации и заполняем форму
    login_page.open()
    login_page.click_create_account_button()

    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.fill('input[name="passwordSubmit"]', password)
    page.click('button:has-text("Sign Up")')

    return username, password


@pytest.fixture
def logged_in_user(page, registered_user):
    """Авторизуем пользователя и переходим на главную страницу"""
    username, password = registered_user
    login_page = LoginPage(page)

    # Входим в систему с зарегистрированными данными
    login_page.open()
    login_page.enter_username(username)
    login_page.enter_password(password)
    login_page.click_login_button()

    # Ждем пока нас перебросит на главную страницу
    page.wait_for_url("**/main", timeout=5000)

    return username, password
