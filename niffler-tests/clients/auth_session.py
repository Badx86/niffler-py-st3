import requests
from urllib.parse import urljoin, parse_qs, urlparse


class AuthSession(requests.Session):
    def __init__(self, auth_url: str):
        super().__init__()
        self.auth_url = auth_url
        self.code = None

    def request(self, method, url, *args, **kwargs):
        # Автоматически добавляем базовый URL, если путь относительный
        full_url = url if url.startswith('http') else urljoin(self.auth_url, url)

        # Выполняем запрос
        response = super().request(method, full_url, *args, **kwargs)

        # "Ловим" code из URL редиректа
        if response.history:
            for resp in response.history:
                if 'code=' in resp.headers.get('Location', ''):
                    parsed_url = urlparse(resp.headers['Location'])
                    query_params = parse_qs(parsed_url.query)
                    self.code = query_params.get('code', [None])[0]
                    break
        return response
