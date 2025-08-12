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
            "gateway_url": "http://localhost:8090",
            "spend_db_url": f"postgresql+psycopg2://postgres:{os.getenv('DB_PASSWORD', 'secret')}"
                            f"@localhost:5432/niffler-spend"
        },
        "docker": {
            "auth_url": "http://auth.niffler.dc:9000",
            "frontend_url": "http://frontend.niffler.dc",
            "gateway_url": "http://gateway.niffler.dc:8090",
            "spend_db_url": f"postgresql+psycopg2://postgres:{os.getenv('DB_PASSWORD', 'secret')}"
                            f"@niffler-all-db:5432/niffler-spend",
            # Параметры для OAuth
            "token_url": "http://auth.niffler.dc:9000/oauth2/token",
            "client_id": "niffler-client",
            "client_secret": os.getenv("CLIENT_SECRET", "secret")
        },
        "staging": {
            "auth_url": f"https://{os.getenv('STAGING_AUTH_HOST', 'auth.niffler-stage.qa.guru')}",
            "frontend_url": f"https://{os.getenv('STAGING_FRONTEND_HOST', 'niffler-stage.qa.guru')}",
            "gateway_url": f"https://{os.getenv('STAGING_API_HOST', 'api.niffler-stage.qa.guru')}",
            "spend_db_url": f"postgresql+psycopg2://postgres:{os.getenv('DB_PASSWORD', 'secret')}"
                            f"@{os.getenv('STAGING_DB_HOST', 'staging-db')}:5432/niffler-spend",
            # Параметры для OAuth
            "token_url": f"https://{os.getenv('STAGING_AUTH_HOST', 'auth.niffler-stage.qa.guru')}/oauth2/token",
            "client_id": "niffler-client",
            "client_secret": os.getenv("CLIENT_SECRET", "secret")
        },
    }

    @classmethod
    def get_env_config(cls, env_name: str = "local") -> dict:
        """
        Получение конфигурации для окружения с приоритетом .env переменных

        Args:
            env_name: имя окружения (local, docker, staging)

        Returns:
            dict: конфигурация с auth_url, frontend_url, gateway_url, spend_db_url
        """
        # Получаем дефолтную конфигурацию
        default_config = cls._DEFAULT_ENVIRONMENTS.get(
            env_name, cls._DEFAULT_ENVIRONMENTS["local"]
        )

        # Проверяем .env переменные (приоритет)
        auth_url_from_env = os.getenv("AUTH_BASE_URL")
        frontend_url_from_env = os.getenv("FRONTEND_BASE_URL")
        gateway_url_from_env = os.getenv("GATEWAY_URL")
        spend_db_url_from_env = os.getenv("SPEND_DB_URL")
        token_url_from_env = os.getenv("TOKEN_URL")
        client_id_from_env = os.getenv("CLIENT_ID")
        client_secret_from_env = os.getenv("CLIENT_SECRET")

        # Если в .env есть URLs - используем их, иначе дефолтные
        return {
            "auth_url": auth_url_from_env or default_config.get("auth_url"),
            "frontend_url": frontend_url_from_env or default_config.get("frontend_url"),
            "gateway_url": gateway_url_from_env or default_config.get("gateway_url"),
            "spend_db_url": spend_db_url_from_env or default_config.get("spend_db_url"),
            "token_url": token_url_from_env or default_config.get("token_url"),
            "client_id": client_id_from_env or default_config.get("client_id"),
            "client_secret": client_secret_from_env or default_config.get("client_secret"),
        }
