import requests


class RequestFailed(Exception):
    def __init__(self, response: requests.Response):
        """
        :param response: объект ответа.
        """
        self.response = response
        self.status_code = response.status_code
        self.url = response.request.url
        self.request_headers = response.request.headers
        if "cookie" in self.request_headers:
            self.request_headers["cookie"] = "HIDDEN"
        self.request_body = response.request.body
        self.log_response = False

    def short_str(self):
        return f"Ошибка запроса к {self.url}. Cтатус-код: {self.status_code})"

    def __str__(self):
        msg = f"Ошибка запроса к {self.url} .\n" \
              f"Метод: {self.response.request.method} .\n" \
              f"Статус-код ответа: {self.status_code} .\n" \
              f"Заголовки запроса: {self.request_headers} .\n" \
              f"Тело запроса: {self.request_body} .\n" \
              f"Текст ответа: {self.response.text}"
        if self.log_response:
            msg += f"\n{self.response.content.decode()}"
        return msg