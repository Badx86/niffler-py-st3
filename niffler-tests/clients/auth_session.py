import requests
import allure

from threading import Lock
from http import HTTPStatus


class OAuthSession(requests.Session):
    """
    Cессия requests, которая автоматически управляет OAuth-токеном
    - Получает токен при первом запросе
    - Обновляет токен при получении 401 ошибки и повторяет запрос
    """

    def __init__(self, token_url: str, client_id: str, client_secret: str):
        # Вызываем конструктор родителя без лишних аргументов
        super().__init__()
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._token_lock = Lock()  # Для безопасной работы в несколько потоков

    def _get_new_token(self):
        """Метод для получения нового токена"""
        with allure.step("Получение нового OAuth токена (client_credentials)"):
            response = requests.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "read write"  # Укажите нужные scopes
                },
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            allure.attach(f"Новый токен успешно получен: {self._access_token[:15]}...", name="New Access Token")

    def request(self, method, url, **kwargs):
        """Переопределенный метод, который перехватывает запросы"""
        # Блокировка, чтобы только один поток мог обновлять токен
        with self._token_lock:
            if not self._access_token:
                self._get_new_token()

        # Добавляем заголовок авторизации в каждый запрос
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self._access_token}'
        kwargs['headers'] = headers

        # Делаем исходный запрос
        response = super().request(method, url, **kwargs)

        # Если токен истек, обновляем его и повторяем запрос один раз
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            allure.step("Токен истек (401 Unauthorized). Запрашиваем новый и повторяем запрос.")
            with self._token_lock:
                self._get_new_token()

            headers['Authorization'] = f'Bearer {self._access_token}'
            kwargs['headers'] = headers
            response = super().request(method, url, **kwargs)

        return response
