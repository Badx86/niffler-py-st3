from playwright.sync_api import Browser, BrowserContext, Page
from clients.spends_client import SpendsHttpClient
from pages.spending_page import SpendingPage
from actions.auth_actions import AuthActions
from builders.user_builder import UserBuilder
from models.data_models import UserData
from pages.login_page import LoginPage
from pages.main_page import MainPage
from data_bases.spend_db import SpendDb
from typing import Generator
from config import Config
from pathlib import Path
import pytest
import allure
import json
import sys
import os


# ===============================
# HOOKS AND CONFIGURATION
# ===============================

def pytest_addoption(parser) -> None:
    """Добавление опций командной строки"""
    parser.addoption(
        "--env",
        action="store",
        default="docker",
        help="Environment: local, docker, staging",
    )


def pytest_configure(config) -> None:
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
    """Автоматические скриншоты и видео при падении тестов"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "page" in item.fixturenames:
            page = item.funcargs["page"]

            # Скриншот
            screenshot_bytes = page.screenshot(full_page=True)
            allure.attach(
                screenshot_bytes,
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

            # Видео
            if page.video:
                video_path = page.video.path()
                if video_path and Path(video_path).exists():
                    allure.attach.file(
                        video_path,
                        name="video",
                        attachment_type=allure.attachment_type.WEBM,
                    )


# =============================
# ENVIRONMENT AND BROWSER SETUP
# =============================

@pytest.fixture(scope="session")
def environment(request) -> dict[str, str]:
    """Получение конфигурации окружения"""
    env_name = request.config.getoption("--env")
    return Config.get_env_config(env_name)


@pytest.fixture(scope="session")
def browser(playwright) -> Generator[Browser, None, None]:
    """Браузер с настройками из .env"""
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = playwright.chromium.launch(headless=headless)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser) -> Generator[BrowserContext, None, None]:
    """Браузер контекст с фиксированным размером окна"""
    # Таймаут из .env или дефолтное значение
    timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))

    # Запись видео только если нужно (через env переменную)
    record_video = os.getenv("RECORD_VIDEO", "false").lower() == "true"

    context_options = {
        "viewport": {"width": 1920, "height": 1080},
    }

    if record_video:
        context_options.update(
            {
                "record_video_dir": "videos/",
                "record_video_size": {"width": 1920, "height": 1080},
            }
        )

    browser_context = browser.new_context(**context_options)
    browser_context.set_default_timeout(timeout)

    yield browser_context
    browser_context.close()


# ===============================
# SHARED AUTHENTICATION
# ===============================

@pytest.fixture(scope="session")
def shared_user() -> UserData:
    """Пользователь для shared авторизации с timestamp для уникальности"""
    import time
    timestamp = int(time.time() % 100000)
    username = f"test_user_{timestamp}"
    return UserBuilder().with_username(username).with_password("TestPass123").build()


@pytest.fixture(scope="session")
def auth_state_file(shared_user: UserData) -> Path:
    """Файл для хранения состояния авторизации"""
    auth_file = Path(".pytest_cache") / f"auth_{shared_user.username}.json"
    auth_file.parent.mkdir(exist_ok=True)
    return auth_file


@pytest.fixture(scope="function")
def authenticated_page(
        browser: Browser,
        auth_state_file: Path,
        shared_user: UserData,
        environment: dict
) -> Generator[Page, None, None]:
    """Оптимизированная shared авторизация с переиспользованием auth state"""
    timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    record_video = os.getenv("RECORD_VIDEO", "false").lower() == "true"

    context_options = {"viewport": {"width": 1920, "height": 1080}}
    if record_video:
        context_options.update({"record_video_dir": "videos/", "record_video_size": {"width": 1920, "height": 1080}})

    main_url = f"{environment['frontend_url']}/main"

    # Попытка переиспользования существующего auth state
    if auth_state_file.exists():
        file_size = auth_state_file.stat().st_size
        if file_size > 100:
            try:
                ctx = browser.new_context(storage_state=str(auth_state_file), **context_options)
                ctx.set_default_timeout(timeout)
                page = ctx.new_page()
                page.goto(main_url)

                if "/main" in page.url:
                    yield page
                    ctx.close()
                    return

                ctx.close()
            except Exception:
                pass

        auth_state_file.unlink(missing_ok=True)

    # Создание нового auth state
    ctx = browser.new_context(**context_options)
    ctx.set_default_timeout(timeout)
    page = ctx.new_page()

    login_page = LoginPage(page, environment)
    auth_actions = AuthActions(login_page)

    try:
        auth_actions.login_user(shared_user.username, shared_user.password)
    except:
        auth_actions.register_user(shared_user.username, shared_user.password)
        auth_actions.login_user(shared_user.username, shared_user.password)

    ctx.storage_state(path=str(auth_state_file))
    yield page
    ctx.close()


# ===============================
# ALLURE REPORTING
# ===============================

@pytest.fixture(scope="session", autouse=True)
def allure_environment(environment: dict) -> None:
    """Настройка информации об окружении для Allure отчетов"""
    properties = [
        f"Environment={environment['frontend_url']}",
        f"Auth_URL={environment['auth_url']}",
        f"Python_Version={sys.version.split()[0]}",
        f"Browser_Timeout={os.getenv('BROWSER_TIMEOUT', '30000')}ms",
        "Browser=Chromium",
        "Framework=Playwright + pytest",
    ]
    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/environment.properties", "w") as f:
        for prop in properties:
            f.write(f"{prop}\n")


# ===============================
# PAGE FIXTURES
# ===============================

@pytest.fixture
def login_page(page: Page, environment: dict) -> LoginPage:
    """Фикстура для страницы авторизации"""
    return LoginPage(page, environment)


@pytest.fixture
def main_page(page: Page, environment: dict) -> MainPage:
    """Фикстура для главной страницы"""
    return MainPage(page, environment)


@pytest.fixture
def spending_page(page: Page, environment: dict) -> SpendingPage:
    """Фикстура для страницы расходов"""
    return SpendingPage(page, environment)


# ===============================
# ACTION AND DATA FIXTURES
# ===============================

@pytest.fixture
def auth_actions(login_page: LoginPage) -> AuthActions:
    """Фикстура для действий авторизации"""
    return AuthActions(login_page)


@pytest.fixture
def user_data() -> UserData:
    """Генерация случайных данных пользователя для каждого теста"""
    return UserBuilder().with_random_credentials().build()


@pytest.fixture
def registered_user(auth_actions: AuthActions, user_data: UserData) -> UserData:
    """Регистрация нового пользователя и возврат его данных"""
    auth_actions.register_user(user_data.username, user_data.password)
    return user_data


@pytest.fixture
def logged_in_user(shared_user: UserData) -> UserData:
    """Используем того же пользователя что в authenticated_page"""
    return shared_user


# ===================
# DB FIXTURES
# ===================

@pytest.fixture
def spend_db(environment: dict) -> SpendDb:
    """Фикстура для работы с БД трат"""
    return SpendDb(environment['spend_db_url'])


@pytest.fixture
def auth_token(authenticated_page: Page) -> str:
    """Получить токен авторизации из браузера"""
    token = authenticated_page.evaluate("() => window.sessionStorage.getItem('id_token')")
    return token or "test_token_placeholder"


@pytest.fixture
def spends_client(environment: dict, auth_token: str) -> SpendsHttpClient:
    """Фикстура для HTTP клиента"""
    return SpendsHttpClient(environment['gateway_url'], auth_token)
