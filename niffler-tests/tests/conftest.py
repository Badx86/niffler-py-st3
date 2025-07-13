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
        default="docker",
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
        "Browser=Chromium",
        "Framework=Playwright + pytest",
    ]

    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/environment.properties", "w") as f:
        for prop in properties:
            f.write(f"{prop}\n")


# ===============================
# SHARED AUTHENTICATION
# ===============================

@pytest.fixture(scope="session")
def auth_storage(tmp_path_factory):
    """Хранилище состояния авторизации для shared auth"""
    return tmp_path_factory.mktemp("session") / "auth_state.json"


@pytest.fixture(scope="session")
def session_user():
    """Пользователь для shared авторизации (создается один раз на сессию)"""
    return UserBuilder().with_random_credentials().build()


@pytest.fixture(scope="function")
def authenticated_page(browser, auth_storage, session_user, environment):
    """Shared auth с простым fallback"""
    timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    record_video = os.getenv("RECORD_VIDEO", "false").lower() == "true"

    base_context_options = {
        "viewport": {"width": 1920, "height": 1080},
    }

    if record_video:
        base_context_options.update(
            {
                "record_video_dir": "videos/",
                "record_video_size": {"width": 1920, "height": 1080},
            }
        )

    # Попытка с storage state
    if auth_storage.exists():
        try:
            # Создаем копию context_options для storage state
            storage_context_options = base_context_options.copy()
            storage_context_options["storage_state"] = str(auth_storage)

            browser_context = browser.new_context(**storage_context_options)
            browser_context.set_default_timeout(timeout)
            page = browser_context.new_page()

            # Используем environment для URL
            main_url = f"{environment['frontend_url']}/main"
            page.goto(main_url)

            # Простая проверка - если не перебросило на логин = ОК
            if "/main" in page.url:
                yield page
                browser_context.close()
                return
            browser_context.close()
        except:
            pass  # Любая ошибка = fresh login

        # Удаляем битый storage
        auth_storage.unlink(missing_ok=True)

    # Fresh login - используем оригинальные context_options без storage_state
    browser_context = browser.new_context(**base_context_options)
    browser_context.set_default_timeout(timeout)
    page = browser_context.new_page()

    login_page = LoginPage(page, environment)
    auth_actions = AuthActions(login_page)
    auth_actions.register_user(session_user.username, session_user.password)
    auth_actions.login_user(session_user.username, session_user.password)

    browser_context.storage_state(path=str(auth_storage))
    yield page
    browser_context.close()


# ==============
# PAGE FIXTURES
# ==============

@pytest.fixture
def login_page(page, request):
    """Фикстура для страницы авторизации"""
    # Пытаемся получить environment, если есть
    try:
        environment = request.getfixturevalue("environment")
    except:
        environment = Config.get_env_config("docker")
    return LoginPage(page, environment)


@pytest.fixture
def main_page(page, request):
    """Фикстура для главной страницы"""
    # Пытаемся получить environment, если есть
    try:
        environment = request.getfixturevalue("environment")
    except:
        environment = Config.get_env_config("docker")
    return MainPage(page, environment)


@pytest.fixture
def spending_page(page, request):
    """Фикстура для страницы расходов"""
    # Пытаемся получить environment, если есть
    try:
        environment = request.getfixturevalue("environment")
    except:
        environment = Config.get_env_config("docker")
    return SpendingPage(page, environment)


# ==================
# ACTION FIXTURES
# ==================

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
