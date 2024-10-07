import datetime
import logging
from typing import List, Dict
import requests

from src.PskovEduAPI import models
from src.PskovEduAPI.common import const, html_parsers
from src.PskovEduAPI.exceptions import RequestFailed, PageNotFound
from src.config import cfg
from src.PskovEduAPI.common.utils import get_monday_date

logger = logging.getLogger(f"PskovEduAPI.{__name__}")


def default_headers():
    return {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.7",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Brave\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "sec-fetch-dest": "empty",
        "x-requested-with": "XMLHttpRequest",
        "upgrade-insecure-requests": "1"
    }


class Client:
    def __init__(self, phpsessid: str, x1: str = None, get_me=False):
        self.phpsessid = phpsessid
        self.x1 = x1

        self.session = requests.Session()
        self.session.cookies.set('phpsessid', self.phpsessid)
        self.session.cookies.set('X1_SSO', '' if not x1 else x1)
        self.me: models.Student = None

        self.headers = default_headers()

        self.__teachers: List[models.Teacher] = []
        """Список учителей"""
        self.__classes: List[models.Class] = []
        """Список школьных классов"""
        self.__periods: List[models.Period] = []
        """Список учебных периодов"""

        if get_me:
            self.get_me()

    def _update_cookies(self, response: requests.Response):
        self.session.cookies.update(response.cookies)
        cfg.set("X1_SSO", self.x1)

    def _prepare_headers(self):
        """
        Подготавливает заголовки запроса
        """
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
        self._post_request(response)
        self.me = html_parsers.extract_student(response.text)

        return self.me

    def _handle_error_response(self, response, json_requied=False):
        """
        Обрабатывает запрос и возбуждает исключение если он неуспешный
        """
        if "ресурс не найден" in response.text.lower():
            raise PageNotFound(response)
        if json_requied and not response.json():
            raise RequestFailed(response)
        if response.status_code != 200 and not response.json()['success']:
            raise RequestFailed(response)
        if "доступ к странице запрещён" in response.text.lower():
            raise RequestFailed(response)

    def _post_request(self, response: requests.Response, **kwargs):
        """
        Обрабатывает запрос после выполнения
        """
        self._update_cookies(response)
        self._handle_error_response(response, **kwargs)

    def base_page(self):
        """
        Получает основную страницу one.pskovedu.ru

        :return: экзепляр requests.Reponse
        """
        headers = self._prepare_headers()
        response = self.session.get(const.BASE_URL, headers=headers)

        self._post_request(response)

        return response

    def fetch_diary(self, date: str = None, indent: int = 0) -> models.Diary:
        """
        Получает дневник ученика (расписание, домашние задания, оценки, ...)


        :param date: Дата. Опционально
        :param indent: отсуп в неделях

        :return: экзепляр класса models.Diary
        """
        if date is None:
            date = get_monday_date(format=None)

            if indent < 0:
                date -= datetime.timedelta(weeks=abs(indent))
            else:
                date += datetime.timedelta(weeks=abs(indent))

            date = date.strftime("%d.%m.%Y")
        url = f"{const.URL_DIARY}/{self.me.guid if self.me else self.get_me().guid}"
        response = self.session.get(url, headers=self._prepare_headers(), params={"date": date})

        self._post_request(response, json_requied=True)

        return models.Diary.from_dict(response.json()['data'])

    def get_grades_report(self, index_period: int = None) -> models.GradesReport:
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
        url = const.URL_GRADES.format(self.me.guid)
        response = self.session.get(url, headers=self._prepare_headers(),
                                    params={"begin": tr.date_begin, "end": tr.date_end, "format": "html"})

        self._post_request(response)

        return html_parsers.html_to_grades(response.text)

    def _direct(self, action: str = "X1API", method: str = "direct", data: list = [], type: str = None,
                tid: int = None) -> requests.Response:
        payload = {
            "action": action,
            "method": method,
            "data": data,
            "type": type or "rpc",
            "tid": tid or 1
        }

        response = self.session.post(const.URL_DIRECT, headers=self._prepare_headers(), json=payload)

        self._post_request(response, json_requied=True)

        return response

    def get_notifications(self) -> List[models.Event]:
        """
        Получает список уведомлений

        :return: List[models.Event]
        """
        data = [{"service": "utility", "method": "getusernotifications",
                 "params": [], "ctx": {}}]
        response = self._direct("getusernotifications", data=data)
        return [models.Event.from_dict(e) for e in response.json()['data']]

    def get_teachers(self) -> List[models.Teacher]:
        """
        Получает список преподавателей

        :return: List[models.Teacher]
        """
        response = self._direct("Scheduler", "getTeachers")
        self._handle_error_response(response)
        teachers = [models.Teacher(e['text'], e['itemId']) for e in response.json()['data']]
        self.__teachers = teachers
        return teachers

    def get_classes(self) -> List[models.Class]:
        """
        Получает список учебных классов

        :return: List[Dict]
        """
        response = self._direct("Reports", "getGrades")
        self._handle_error_response(response)
        classes = [models.Class(c["alltext"], c['itemId']) for c in response.json()['data']]
        self.__classes = classes
        return classes

    def get_years(self) -> List[Dict]:
        """
        Получает список лет

        :return: List[Dict]
        """
        response = self._direct("Reports", "getYears")
        return response.json()['data']

    def get_periods(self) -> List[models.Period]:
        """
        Получает список периодов учебы

        :return: List[Dict]
        """
        response = self._direct("Reports", "getPeriods")
        self._handle_error_response(response)
        periods = [models.Period.from_dict(p) for p in response.json()['data']]
        self.__periods = periods
        return periods

    def get_grade_types(self) -> List[Dict]:
        """
        Получает список типов оценок

        :return: List[Dict]
        """
        response = self._direct("Reports", "getGradeTypes")
        return response.json()['data']

    def get_mark_types(self) -> List[Dict]:
        """
        Получает список типов оценок

        :return: List[Dict]
        """
        response = self._direct("Reports", "getMarkTypes")
        return response.json()['data']

    def get_participants(self) -> List[Dict]:
        """
        Получает список участников
        Доступно только для сотрудников!

        :return: List[Dict]
        """
        response = self._direct("Reports", "getParticipants")
        return response.json()['data']

    def get_journals(self) -> List[Dict]:
        """
        Получает список журналов
        Доступно только для сотрудников!

        :return: List[Dict]
        """
        response = self._direct("Scheduler", "getJournals")
        return response.json()['data']

    def read_journal(self, journal_id: int) -> Dict:
        """
        Получает журнал по его ID
        Доступно только для сотрудников!

        :param journal_id: ID журнала
        :return: Dict
        """
        data = [{"name": "getJournal", "params": [journal_id]}]
        response = self._direct("JournalService", "getJournal", data=data)
        return response.json()['data']

    def save_journal(self) -> Dict:
        """
        Сохраняет журнал
        Доступно только для сотрудников!

        :return: Dict
        """
        response = self._direct("JournalService", "save")
        return response.json()['data']

    def delete_journal(self, journal_id: int) -> Dict:
        """
        Удаляет журнал по его ID
        Доступно только для сотрудников!

        :param journal_id: ID журнала
        :return: Dict
        """
        data = [{"name": "deleteJournal", "params": [journal_id]}]
        response = self._direct("JournalService", "deleteJournal", data=data)
        return response.json()['data']

    def get_reception(self, start: str, end: str, type: str) -> Dict:
        """
        Получает данные о приеме

        :param start: Начальная дата
        :param end: Конечная дата
        :param type: Тип приема
        :return: Dict
        """
        data = [{"name": "getReception", "params": [start, end, type]}]
        response = self._direct("Reception", "getReception", data=data)
        return response.json()['data']

    def read_monitoring(self, grades: List[int]) -> Dict:
        """
        Читает данные мониторинга

        :param grades: Список оценок
        :return: Dict
        """
        data = [{"name": "read", "params": [grades]}]
        response = self._direct("monitoring", "read", data=data)
        return response.json()['data']

    def read_skip_monitoring(self, part: int) -> Dict:
        """
        Читает данные мониторинга пропусков
        Доступно только для сотрудников!

        :param part: Часть данных
        :return: Dict
        """
        data = [{"name": "readskip", "params": [part]}]
        response = self._direct("monitoring", "readskip", data=data)
        return response.json()['data']

    def show_performance_by_grade(self) -> Dict:
        """
        Показывает производительность по оценкам
        Доступно только для сотрудников!

        :return: Dict
        """
        response = self._direct("ES\\Controller\\ReportController", "showPerformanceByGrade")
        return response.json()['data']

    # todo:
    # Запрос которые отправляются по отдельным ссылкам
    # https:/one.pskovedu.ru/{Путь для запроса}
    # Возвращают requests.Response
    # По факту, это просто переход по нужной ссылке, без получения каких то данных
    # Может быть полезно, есло нужно получить данные из HTML кода страницы
    # Вернут результат, только если роль пользователя есть в спике доступных

    def page_schedule(self) -> requests.Response:
        """
        Получает страницу с получением расписания занятий

        Название: Расписание занятий
        Роли (EN): admin, zavuch, classruk, teacher, participant
        Роли (RU): администратор, завуч, классный руководитель, учитель, участник
        Путь: /schedule/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SCHEDULE, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_edu_topics(self) -> requests.Response:
        """
        Получает страницу с тематическоим планированием

        Название: Тематическое планирование
        Роли (EN): teacher, admin, zavuch
        Роли (RU): учитель, администратор, завуч
        Путь: /eje/topics/journals

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_EDU_TOPICS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_diary(self) -> requests.Response:
        """
        Получает дневник учащегося

        Название: Дневник учащегося
        Роли (EN): parents, participant
        Роли (RU): родители, участник
        Путь: /edv/index/participant

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_DIARY, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_calendar(self) -> requests.Response:
        """
        Получает календарь событий

        Название: Календарь событий
        Роли (EN): admin, zavuch, classruk, teacher, parents, participant
        Роли (RU): администратор, завуч, классный руководитель, учитель, родители, участник
        Путь: /calendar/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_CALENDAR, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_desk(self) -> requests.Response:
        """
        Получает доску объявлений

        Название: Доска объявлений
        Роли (EN): admin, zavuch, parents, participant, teacher, participant
        Роли (RU): администратор, завуч, родители, участник, учитель, участник
        Путь: /desk/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_DESK, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_substitutions(self) -> requests.Response:
        """
        Получает журнал замещений

        Название: Журнал замещений
        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /esp/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SUBSTITUTIONS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_diaries(self) -> requests.Response:
        """
        Получает дневники

        Название: Дневники
        Роли (EN): admin, zavuch, classruk
        Роли (RU): администратор, завуч, классный руководитель
        Путь: /edv/index/school

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_DIARIES, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_school_reports(self) -> requests.Response:
        """
        Получает отчеты

        Название: Отчеты
        Роли (EN): admin, zavuch, classruk, teacher
        Роли (RU): администратор, завуч, классный руководитель, учитель
        Путь: /er/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SCHOOL_REPORTS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_school_stat(self) -> requests.Response:
        """
        Получает статистику по школе

        Название: Статистика по школе
        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/school-stat/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SCHOOL_STAT, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_parents(self) -> requests.Response:
        """
        Получает родителей

        Название: Родители
        Роли (EN): admin, zavuch, classruk
        Роли (RU): администратор, завуч, классный руководитель
        Путь: /eje/parents-registrations/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_PARENTS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_teachers_admin(self) -> requests.Response:
        """
        Получает учителей, только для указанных ролей (можно использовать метод "get_teachers", тогда можно получить в не зависимости от роли)

        Название: Учителя
        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/teachers-registrations/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_TEACHERS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_doo_group_control(self) -> requests.Response:
        """
        Получает управление дошкольными группами

        Роли (EN): admin, zavuch, uo, muo
        Роли (RU): администратор, завуч, уо, муо
        Путь: /dooservice/control/group-select

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_DOO_GROUP_CONTROL, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_doo_assignment(self) -> requests.Response:
        """
        Получает комплектование ДОО

        Роли (EN): muo_kg_operator
        Роли (RU): оператор муо_кг
        Путь: /dooservice/assignment/index

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_DOO_ASSIGNMENT, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_schedule_templates(self) -> requests.Response:
        """
        Получает шаблоны расписания

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /est/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SCHEDULE_TEMPLATES, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_schedule_generation(self) -> requests.Response:
        """
        Получает генерацию расписания

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /esg/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SCHEDULE_GENERATION, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_participants_migration(self) -> requests.Response:
        """
        Получает перенос оценок

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /epm/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_PARTICIPANTS_MIGRATION, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_exam_results(self) -> requests.Response:
        """
        Получает результаты тестирования

        Роли (EN): admin, zavuch, classruk, participant, parents
        Роли (RU): администратор, завуч, классный руководитель, участник, родители
        Путь: /ear/exam-results/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_EXAM_RESULTS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_participants_info(self) -> requests.Response:
        """
        Получает дополнительную информацию об участниках

        Роли (EN): admin, zavuch, classruk
        Роли (RU): администратор, завуч, классный руководитель
        Путь: /eje/participants-info/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_PARTICIPANTS_INFO, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_gradehead_comments(self) -> requests.Response:
        """
        Получает заметки

        Роли (EN): zavuch, classruk, teacher, parents, participant
        Роли (RU): завуч, классный руководитель, учитель, родители, участник
        Путь: /eje/grade-head-comments/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_GRADEHEAD_COMMENTS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_subscriptions_management(self) -> requests.Response:
        """
        Получает услуги

        Роли (EN): parents, participant
        Роли (RU): родители, участник
        Путь: /esm/index

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SUBSCRIPTIONS_MANAGEMENT, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_mark_type_migration(self) -> requests.Response:
        """
        Получает изменение системы оценивания журнала

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/mark-type-migration/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_MARK_TYPE_MIGRATION, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_journal_generation(self) -> requests.Response:
        """
        Получает генерацию журналов

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/journal-generation/grade-select

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_JOURNAL_GENERATION, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_edu_plans_generation(self) -> requests.Response:
        """
        Получает генерацию учебных планов

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/plan-generation/grade-select

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_EDU_PLANS_GENERATION, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_period_marks_transfer(self) -> requests.Response:
        """
        Получает перенос итоговых оценок

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /ear/period-marks-transfer/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_PERIOD_MARKS_TRANSFER, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_participant_marks_history(self) -> requests.Response:
        """
        Получает историю оценок участников

        Роли (EN): admin, zavuch, classruk
        Роли (RU): администратор, завуч, классный руководитель
        Путь: /eje/participant-marks-history/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_PARTICIPANT_MARKS_HISTORY, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_admin_applications_spo(self) -> requests.Response:
        """
        Получает заявления в СПО

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /es/index/incoming/profstatements

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_ADMIN_APPLICATIONS_SPO, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_confirmed_measures(self) -> requests.Response:
        """
        Получает контрольные и диагностические работы

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/measures/list

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_CONFIRMED_MEASURES, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_grade_types_full(self) -> requests.Response:
        """
        Получает типы оценок

        Роли (EN): admin, zavuch
        Роли (RU): администратор, завуч
        Путь: /eje/grade-types/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_GRADE_TYPES, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_journal_control(self) -> requests.Response:
        """
        Получает проверку журналов

        Роли (EN): teacher, admin, zavuch
        Роли (RU): учитель, администратор, завуч
        Путь: /ejc/index/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_JOURNAL_CONTROL, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_acl(self) -> requests.Response:
        """
        Получает настройку прав доступа

        Роли (EN): sysadmin
        Роли (RU): системный администратор
        Путь: /eje/access-control/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_ACL, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_users(self) -> requests.Response:
        """
        Получает пользователей

        Роли (EN): sysadmin
        Роли (RU): системный администратор
        Путь: /eje/admin-impersonation/

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_USERS, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_counters_view(self) -> requests.Response:
        """
        Получает показатели

        Роли (EN): sysadmin
        Роли (RU): системный администратор
        Путь: /eje/counters-view

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_COUNTERS_VIEW, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_subscriptions_send(self) -> requests.Response:
        """
        Получает услуги (sysadmin)

        Роли (EN): sysadmin
        Роли (RU): системный администратор
        Путь: /esm/index/sysadmin

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_SUBSCRIPTIONS_SEND, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_period_stat(self) -> requests.Response:
        """
        Получает отчет по успеваемости по региону

        Роли (EN): sysadmin
        Роли (RU): системный администратор
        Путь: /eje/period-stat

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_PERIOD_STAT, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_applications_spo(self) -> requests.Response:
        """
        Получает заявления в СПО

        Путь: https://www.gosuslugi.ru/10171/1/form

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_APPLICATIONS_SPO, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_applications_oo(self) -> requests.Response:
        """
        Получает заявления в ОО

        Путь: https://statements.pskovedu.ru

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_APPLICATIONS_OO, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_statements_gia(self) -> requests.Response:
        """
        Получает запись на ГИА

        Путь: /service/service-not-available

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_STATEMENTS_GIA, headers=self._prepare_headers())
        self._post_request(response)
        return response

    def page_conflicts(self) -> requests.Response:
        """
        Получает результаты и апелляции ГИА

        Путь: https://conflicts.pskovedu.ru

        :return: экзепляр requests.Response
        """
        response = self.session.get(const.URL_CONFLICTS, headers=self._prepare_headers())
        self._post_request(response)
        return response
