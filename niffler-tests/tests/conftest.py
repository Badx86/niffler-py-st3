from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.spending_page import SpendingPage
from actions.auth_actions import AuthActions
from builders.user_builder import UserBuilder
from config import Config
import pytest
import allure
import json
import sys
import os
from pathlib import Path


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
    """Автоматические скриншоты и видео при падении тестов"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "page" in item.fixturenames:
            page = item.funcargs["page"]

            # Скриншот
            screenshot_bytes = page.screenshot()
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
def environment(request):
    """Получение конфигурации окружения"""
    env_name = request.config.getoption("--env")
    return Config.get_env_config(env_name)


@pytest.fixture(scope="session")
def browser(playwright):
    """Браузер с настройками из .env"""
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = playwright.chromium.launch(headless=headless)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    """Браузер контекст с фиксированным размером окна"""
    # Таймаут из .env или дефолтное значение
    timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))

    # Запись видео только если включено в .env
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

    context = browser.new_context(**context_options)
    context.set_default_timeout(timeout)

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
        f"Browser_Timeout={os.getenv('BROWSER_TIMEOUT', '30000')}ms",
        f"Headless={os.getenv('HEADLESS', 'true')}",
        f"Record_Video={os.getenv('RECORD_VIDEO', 'false')}",
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


@pytest.fixture
def auth_actions(login_page):
    """Фикстура для действий авторизации"""
    return AuthActions(login_page)


# ===================
# USER DATA FIXTURES
# ===================


@pytest.fixture
def user_data():
    """Генерация случайных данных пользователя для каждого теста"""
    return UserBuilder().with_random_credentials().build()


@pytest.fixture
def registered_user(auth_actions, user_data):
    """Регистрация нового пользователя и возврат его данных"""
    auth_actions.register_user(user_data.username, user_data.password)
    return user_data


@pytest.fixture
def logged_in_user(auth_actions, registered_user):
    """Авторизация пользователя и переход на главную страницу"""
    auth_actions.login_user(registered_user.username, registered_user.password)
    return registered_user
