import os
from datetime import datetime, timedelta

from src.PskovEduAPI import models
from src.PskovEduAPI.common.utils import get_monday_date

import logging

logger = logging.getLogger(f"utils.{__name__}")


WEEKDAYS = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}


def create_dirs():
    """
    Создает необходимые директории, если они отсутствуют.
    """
    dirs = [
        "storage/logs",
        "storage/cache",
    ]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

def weekdays(date: datetime = None) -> list[datetime]:
    """
    Возвращает список дат всех будних дней недели, к которой принадлежит указанная дата.

    :param date: дата

    :return: datetime
    """
    men = get_monday_date(None, date)
    return [men + timedelta(days=i) for i in range(5)]

def start_log(user: models.Student, grades_report: models.GradesReport):
    """
    Выводит начальное сообщения при запуске скрипта
    """
    logger.info("============================")
    logger.info(f"$CYANПривет, {user.name}!")
    logger.info(f"$CYANШкола, Класс: {user.school}, {user.class_name}")
    logger.info(f"Текущие оценки:")
    for subject in grades_report.subjects:
        logger.info(f"• {subject.name}: $YELLOW{', '.join(list(map(str, subject.grades)))}")

    logger.info("============================")

def get_weekday(number: int):
    """
    Получает название для недели из числа
    """
    return WEEKDAYS.get(number)


