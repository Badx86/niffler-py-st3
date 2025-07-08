import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # URLs для разных окружений
    ENVIRONMENTS = {
        "local": {
            "auth_url": "http://localhost:9000",
            "frontend_url": "http://localhost:3000",
        },
        "docker": {
            "auth_url": "http://auth.niffler.dc:9000",
            "frontend_url": "http://frontend.niffler.dc:3000",
        },
        "staging": {
            "auth_url": "https://auth.niffler-stage.qa.guru",
            "frontend_url": "https://niffler-stage.qa.guru",
        },
    }

    @classmethod
    def get_env_config(cls, env_name: str = "local"):
        return cls.ENVIRONMENTS.get(env_name, cls.ENVIRONMENTS["local"])

    # Переменные из .env
    AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://localhost:9000")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

    # Эндпоинты
    LOGIN_ENDPOINT = "/login"
    REGISTER_ENDPOINT = "/register"
