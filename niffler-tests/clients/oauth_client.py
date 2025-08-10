import pkce
import allure
from urllib.parse import urljoin
from pydantic import BaseModel, Field
from clients.auth_session import AuthSession


class OAuthRequest(BaseModel):
    response_type: str = Field(default="code")
    client_id: str = Field(default="client")
    scope: str = Field(default="openid")
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str = Field(default="S256")


class OAuthClient:
    """Авторизация по OAuth 2.0 (Authorization Code Flow with PKCE)"""

    def __init__(self, config: dict):
        self.session = AuthSession(auth_url=config["auth_url"])
        self.redirect_uri = urljoin(config["frontend_url"], '/authorized')
        self.token = None
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()

    def get_token(self, username: str, password: str) -> str:
        """Получение access_token путем симуляции логина пользователя"""
        with allure.step("Шаг 1: Запрос на страницу авторизации для получения cookies"):
            self.session.get(
                url='/oauth2/authorize',
                params=OAuthRequest(
                    redirect_uri=self.redirect_uri,
                    code_challenge=self.code_challenge
                ).model_dump(),
                allow_redirects=True
            )

        with allure.step("Шаг 2: POST-запрос на логин с учетными данными и XSRF-TOKEN"):
            self.session.post(
                url='/login',
                data={
                    'username': username,
                    'password': password,
                    '_csrf': self.session.cookies.get('XSRF-TOKEN'),
                },
                allow_redirects=True
            )

        with allure.step("Шаг 3: Обмен полученного 'code' на 'access_token'"):
            token_response = self.session.post(
                url='/oauth2/token',
                data={
                    'code': self.session.code,
                    'redirect_uri': self.redirect_uri,
                    'code_verifier': self.code_verifier,
                    'grant_type': 'authorization_code',
                    'client_id': 'client'
                }
            )
            token_response.raise_for_status()
            self.token = token_response.json().get('access_token')
            if not self.token:
                raise ValueError("Не удалось получить access_token из ответа сервера")
            return self.token
