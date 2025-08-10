from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from clients.spends_client import SpendsHttpClient
from clients.oauth_client import OAuthClient
from pages.spending_page import SpendingPage
from actions.auth_actions import AuthActions
from builders.user_builder import UserBuilder
from pytest import FixtureDef, FixtureRequest
from models.data_models import UserData
from pages.login_page import LoginPage
from pages.main_page import MainPage
from data_bases.spend_db import SpendDb
from typing import Generator
from urllib.parse import urljoin

from config import Config
from pathlib import Path
import pytest
import allure
import json
import sys
import os
import time


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


def allure_logger(config):
    """Получение Allure логгера"""
    listener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item):
    """Автоматическое название тестов в Allure"""
    yield
    allure.dynamic.title(" ".join(item.name.split("_")[1:]).title())


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}]" + " ".join(fixturedef.argname.split("_")).title()


# =============================
# ENVIRONMENT AND BROWSER SETUP
# =============================

@pytest.fixture(scope="session")
def environment(request) -> dict[str, str]:
    """Получение конфигурации окружения"""
    with allure.step("[S] Get Environment Configuration"):
        env_name = request.config.getoption("--env")
        config = Config.get_env_config(env_name)
        allure.attach(json.dumps(config, indent=2), name="Environment Config",
                      attachment_type=allure.attachment_type.JSON)
        return config


@pytest.fixture(scope="session")
def browser(playwright) -> Generator[Browser, None, None]:
    """Браузер с настройками из .env"""
    with allure.step("[S] Launch Browser"):
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = playwright.chromium.launch(headless=headless)
        allure.attach(f"Browser launched: Chromium (headless={headless})", name="Browser Info")
        yield browser
    with allure.step("[S] Close Browser"):
        browser.close()


@pytest.fixture(scope="function")
def context(browser) -> Generator[BrowserContext, None, None]:
    """Браузер контекст с фиксированным размером окна"""
    with allure.step("[F] Create Browser Context"):
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
        allure.attach(json.dumps(context_options, indent=2), name="Context Options",
                      attachment_type=allure.attachment_type.JSON)
        yield browser_context
    with allure.step("[F] Close Browser Context"):
        browser_context.close()


# ===============================
# SHARED AUTHENTICATION
# ===============================

@pytest.fixture(scope="session")
def shared_user() -> UserData:
    """Пользователь для shared авторизации с timestamp для уникальности"""
    with allure.step("[S] Generate Shared User Data"):
        timestamp = int(time.time() % 100000)
        username = f"test_user_{timestamp}"
        user = UserBuilder().with_username(username).with_password("TestPass123").build()
        allure.attach(f"Username: {user.username}", name="Shared User")
        return user


@pytest.fixture(scope="session")
def auth_state_file(shared_user: UserData) -> Path:
    """Файл для хранения состояния авторизации"""
    with allure.step("[S] Prepare Auth State File"):
        auth_file = Path(".pytest_cache") / f"auth_{shared_user.username}.json"
        auth_file.parent.mkdir(exist_ok=True)
        allure.attach(f"Auth state file path: {auth_file}", name="Auth State File Info")
        return auth_file


@pytest.fixture(scope="function")
def authenticated_page(
        browser: Browser,
        auth_state_file: Path,
        shared_user: UserData,
        environment: dict
) -> Generator[Page, None, None]:
    """
    Эта фикстура гарантирует, что пользователь залогинен в браузере
    """
    if auth_state_file.exists():
        context = browser.new_context(storage_state=auth_state_file)
        page = context.new_page()
        page.goto(urljoin(environment["frontend_url"], "/main"))
        # Простая проверка, что мы действительно залогинены
        try:
            page.locator('a[href*="/people"]').wait_for(timeout=3000)
            yield page
            context.close()
            return
        except Exception:
            context.close()
            auth_state_file.unlink()

    # Если state-файл не существует или невалиден, создаем новый
    context = browser.new_context()
    page = context.new_page()
    login_page = LoginPage(page, environment)
    auth_actions = AuthActions(login_page)
    try:
        # Пытаемся залогиниться
        auth_actions.login_user(shared_user.username, shared_user.password)
    except Exception:
        # Если не получилось - регистрируемся и логинимся снова
        auth_actions.register_user(shared_user.username, shared_user.password)
        auth_actions.login_user(shared_user.username, shared_user.password)

    context.storage_state(path=auth_state_file)
    yield page
    context.close()


# ===============================
# PAGE FIXTURES
# ===============================

@pytest.fixture
def login_page(page: Page, environment: dict) -> LoginPage:
    return LoginPage(page, environment)


@pytest.fixture
def main_page(authenticated_page: Page, environment: dict) -> MainPage:
    return MainPage(authenticated_page, environment)


@pytest.fixture
def spending_page(authenticated_page: Page, environment: dict) -> SpendingPage:
    return SpendingPage(authenticated_page, environment)


# ===============================
# ACTION AND DATA FIXTURES
# ===============================

@pytest.fixture
def auth_actions(login_page: LoginPage) -> AuthActions:
    return AuthActions(login_page)


@pytest.fixture
def user_data() -> UserData:
    return UserBuilder().with_random_credentials().build()


@pytest.fixture
def logged_in_user(shared_user: UserData) -> UserData:
    with allure.step("[F] Use Logged In Shared User"):
        allure.attach(f"Using shared user: {shared_user.username}", name="Logged In User Info")
        return shared_user


# ===================
# DB AND API FIXTURES
# ===================

@pytest.fixture
def spend_db(environment: dict) -> SpendDb:
    with allure.step("[F] Connect to Spend Database"):
        db = SpendDb(environment['spend_db_url'])
        allure.attach(f"Connected to DB: {environment['spend_db_url']}", name="DB Connection")
        return db


@pytest.fixture(scope="session")
def api_token(environment: dict, shared_user: UserData) -> str:
    """
    Получает токен для API через полный цикл OAuth 2.0
    """
    with allure.step("[S] Получение API токена через OAuth 2.0 PKCE"):
        oauth_client = OAuthClient(config=environment)
        try:
            token = oauth_client.get_token(shared_user.username, shared_user.password)
        except Exception:
            # Если логин не удался, значит пользователя нет. Регистрируем его через UI.
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                login_page = LoginPage(page, environment)
                auth_actions = AuthActions(login_page)
                auth_actions.register_user(shared_user.username, shared_user.password)
                browser.close()
            # Повторяем попытку получения токена
            token = oauth_client.get_token(shared_user.username, shared_user.password)

        allure.attach(f"Токен получен: {token[:15]}...", name="API Access Token")
        return token


@pytest.fixture
def spends_client(environment: dict, api_token: str) -> SpendsHttpClient:
    """Фикстура для HTTP клиента, использующая токен, полученный по OAuth"""
    with allure.step("[F] Initialize Spends HTTP Client"):
        client = SpendsHttpClient(environment['gateway_url'], token=api_token)
        return client
