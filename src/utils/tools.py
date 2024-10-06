import os
from datetime import datetime, timedelta

from src.PskovEduAPI import models

import logging

logger = logging.getLogger(f"utils.{__name__}")

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

def get_monday_date(format="%d.%m.%Y", time=None) -> str | datetime:
    """
    Возвращает дату понедельника текущей недели в формате "dd.mm.yyyy".

    :param format: Формат времени. Если None, то возвращется datetime
    :param time: Время от которого считать текущую неделю. Опционально

    """
    today = time or datetime.today()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime(format) if format else monday

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


