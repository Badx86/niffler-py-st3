from playwright.sync_api import sync_playwright
import pytest
import os
from mimesis import Person
from pages.login_page import LoginPage


@pytest.fixture(scope="session", autouse=True)
def create_output_directory():
    # Путь к директории для скриншотов
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    # Создание директории, если она еще не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright):
    print('\nstart browser...')
    browser = playwright.chromium.launch(headless=False)
    yield browser
    print('\nquit browser...')
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def user_data():
    """Генерация данных пользователя"""
    person = Person()
    username = person.username() + str(person.identifier(mask='###'))
    password = person.password(length=10)
    return username, password


@pytest.fixture
def registered_user(page, user_data):
    """Регистрация пользователя"""
    username, password = user_data
    login_page = LoginPage(page)

    # Регистрация
    login_page.open()
    login_page.click_create_account_button()

    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.fill('input[name="passwordSubmit"]', password)
    page.click('button:has-text("Sign Up")')

    return username, password


@pytest.fixture
def logged_in_user(page, registered_user):
    """Авторизованный пользователь"""
    username, password = registered_user
    login_page = LoginPage(page)

    # Авторизация
    login_page.open()
    login_page.enter_username(username)
    login_page.enter_password(password)
    login_page.click_login_button()

    # Ожидание редиректа на главную страницу
    page.wait_for_url("**/main", timeout=5000)

    return username, password
