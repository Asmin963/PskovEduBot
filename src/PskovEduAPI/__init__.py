import datetime
import logging
from typing import List, Any

import requests
from cloudscraper import create_scraper

from src.PskovEduAPI import html_parsers, models, const
from src.PskovEduAPI.exceptions import RequestFailed
from src.PskovEduAPI.models import Student
from src.config import cfg
from src.utils import tools

logger = logging.getLogger(f"PskovEduAPI.{__name__}")


def default_headers():
    return {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.7",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Brave\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "x-requested-with": "XMLHttpRequest"
    }


class Client:
    def __init__(self, phpsessid: str, x1: str = None):
        self.phpsessid = phpsessid
        self.x1 = x1

        self.session = create_scraper()
        self.session.cookies.set('phpsessid', self.phpsessid)
        self.session.cookies.set('X1_SSO', '' if not x1 else x1)
        self.me: Student = None

        self.headers = default_headers()

        self.get_me()

    def _update_cookies(self, response: requests.Response):
        self.session.cookies.update(response.cookies)
        cfg.set("X1_SSO", self.x1)

    def _prepare_headers(self):
        h = self.headers
        h['cookie'] = f"PHPSESSID={self.phpsessid}"
        if self.x1:
            h['cookie'] += f"; X1_SSO={self.x1}"
        return h

    def get_me(self) -> models.Student:
        """
        Получает информацию о текущем аккаунте (ученике)

        :return: экзепляр класса models.Student
        """
        response = self.session.get(const.URL_PARTICIPANT, headers=self._prepare_headers())

        self.me = html_parsers.extract_student(response.text)

        self._post_request(response)

        return self.me

    def _handle_error_response(self, response, json_requied=False):
        try:
            if json_requied and not response.json()['success']:
                raise Exception
        except:
            raise RequestFailed(response)

    def _post_request(self, response: requests.Response, **kwargs):
        self._update_cookies(response)
        self._handle_error_response(response, **kwargs)


    def fetch_diary(self, date: str = None, indent: int = 0) -> models.Diary:
        """
        Получает дневник ученика (расписание, домашние задания, оценки, ...)


        :param date: Дата. Опционально
        :param indent: отсуп в неделях

        :return: экзепляр класса models.Diary
        """
        if date is None:
            date = tools.get_monday_date(format=None)

            if indent < 0:
                date -= datetime.timedelta(weeks=abs(indent))
            else:
                date += datetime.timedelta(weeks=abs(indent))

            date = date.strftime("%d.%m.%Y")
        url = f"{const.URL_DIARY}{self.me.guid if self.me else self.get_me().guid}"
        response = self.session.get(url, headers=self._prepare_headers(), params={"date": date})

        self._post_request(response)

        return models.Diary.from_dict(response.json()['data'])

    def get_grades(self, index_period: int = None) -> models.GradesReport:
        """
        Получает отчет об успеваемости

        :param index_period: период, начиная с 1. Опционально

        :return: экзепляр класса models.GradesRrsport
        """
        if index_period is None:
            index_period = 1
        index_period -= 1

        d = self.fetch_diary()
        tr = d.edu_periods[1:][index_period]
        url = f"{const.URL_GRADES}{self.me.guid}/"
        response = self.session.get(url, headers=self._prepare_headers(),
                                    params={"begin": tr.date_begin, "end": tr.date_end, "format": "html"})

        self._post_request(response)

        return html_parsers.html_to_grades(response.text)

    def _direct(self, method, service: str = None, params: List[Any] = None, type: str = None, tid: int = None) -> requests.Response:
        payload = {"action": "X1API", "method": "direct",
                   "data": [{"service": service or "utility", "method": method,
                             "params": params or [], "ctx": {}}],
                   "type": type or "rpc", "tid": tid or 1}
        response = self.session.post(const.URL_DIRECT, headers=self._prepare_headers(), json=payload)

        self._post_request(response, json_requied=True)

        return response

    def get_notifications(self) -> List[models.Event]:
        """
        Получает список уведомлений

        :return: List[models.Event]
        """
        response = self._direct("getusernotifications")
        return [models.Event.from_dict(e) for e in response.json()['data']]

