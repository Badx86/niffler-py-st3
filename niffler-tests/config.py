import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Эндпоинты
    LOGIN_ENDPOINT = "/login"
    REGISTER_ENDPOINT = "/register"

    # Дефолтные URLs для разных окружений (fallback)
    _DEFAULT_ENVIRONMENTS = {
        "local": {
            "auth_url": "http://localhost:9000",
            "frontend_url": "http://localhost:3000",
        },
        "docker": {
            "auth_url": "http://auth.niffler.dc:9000",
            "frontend_url": "http://frontend.niffler.dc",
        },
        "staging": {
            "auth_url": "https://auth.niffler-stage.qa.guru",
            "frontend_url": "https://niffler-stage.qa.guru",
        },
    }

    @classmethod
    def get_env_config(cls, env_name: str = "local") -> dict:
        """
        Получение конфигурации для окружения с приоритетом .env переменных

        Args:
            env_name: имя окружения (local, docker, staging)

        Returns:
            dict: конфигурация с auth_url и frontend_url
        """
        # Получаем дефолтную конфигурацию
        default_config = cls._DEFAULT_ENVIRONMENTS.get(
            env_name, cls._DEFAULT_ENVIRONMENTS["local"]
        )

        # Проверяем .env переменные (приоритет!)
        auth_url_from_env = os.getenv("AUTH_BASE_URL")
        frontend_url_from_env = os.getenv("FRONTEND_BASE_URL")

        # Если в .env есть URLs - используем их, иначе дефолтные
        return {
            "auth_url": auth_url_from_env or default_config["auth_url"],
            "frontend_url": frontend_url_from_env or default_config["frontend_url"],
        }
