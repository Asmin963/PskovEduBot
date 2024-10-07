import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..PskovEduAPI.models import Lesson, Diary

SCHEDULE_FILE_PATH = os.path.join(os.path.abspath(__file__), "..", "..", "..", "storage", "schedules.json")


def _save_schedule(schedule: Dict[str, Dict[str, List[Lesson]]]) -> None:
    """
    Сохраняет расписание в файл
    """
    with open(SCHEDULE_FILE_PATH, 'w', encoding="utf-8") as file:
        json.dump(schedule, file, default=lambda x: x.to_dict(), indent=4, ensure_ascii=False)


def load_schedule():
    """
    Загружает расписание из файла
    """
    if not os.path.exists(SCHEDULE_FILE_PATH):
        return {}

    with open(SCHEDULE_FILE_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_diary_to_schedule(diary: Diary) -> None:
    """
    Добавляет расписание из объекта Diary в файл.
    """
    week_start_date = None
    for day, lessons in diary.days.items():
        if "Понедельник" in day:
            week_start_date = lessons[0].date
            break

    if not week_start_date:
        raise ValueError("Не удалось определить дату начала недели")

    weekly_schedule = {day: lessons for day, lessons in diary.days.items()}

    save_weekly_schedule(week_start_date, weekly_schedule)


def get_schedule_by_day(day: str) -> Optional[Dict[str, List[Lesson]]]:
    """
    Получает расписание по дню
    """
    data = load_schedule()

    for week, schedule in data.items():
        if day in schedule:
            return {day: [Lesson.from_dict(lesson) for lesson in schedule[day]]}

    return None


def save_weekly_schedule(week_start_date: str, schedule: Dict[str, List[Lesson]]) -> None:
    """
    Сохраняет расписание по неделям
    """
    data = load_schedule()

    week_key = f"{week_start_date} - {get_week_end_date(week_start_date)}"

    if week_key in data:
        data[week_key] = {day: [lesson.to_dict() for lesson in lessons] for day, lessons in schedule.items()}
    else:
        data = insert_week_in_order(data, week_key, schedule)

    with open(SCHEDULE_FILE_PATH, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return data


def get_week_end_date(week_start_date: str) -> str:
    """
    Возвращает дату конца недели на основе даты начала недели
    """
    start_date = datetime.strptime(week_start_date, "%d.%m.%Y")
    end_date = start_date + timedelta(days=6)
    return end_date.strftime("%d.%m.%Y")


def insert_week_in_order(data: Dict[str, Dict[str, List[Lesson]]], week_key: str, schedule: Dict[str, List[Lesson]]) -> \
Dict[str, Dict[str, List[Lesson]]]:
    """
    Вставляет новую неделю в правильное место в расписании.

    :param data: Текущее расписание (словарь, где ключи — недели, значения — расписание по дням)
    :param week_key: Ключ для новой недели (строка в формате "dd.mm.yyyy - dd.mm.yyyy")
    :param schedule: Расписание для новой недели (словарь, где ключи — дни, значения — список уроков)
    :return: Обновленное расписание с новой неделей, вставленной в правильное место
    """
    new_data = {}
    inserted = False
    for existing_week, existing_schedule in data.items():
        if not inserted and existing_week > week_key:
            new_data[week_key] = {day: [lesson.to_dict() for lesson in lessons] for day, lessons in schedule.items()}
            inserted = True
        new_data[existing_week] = existing_schedule

    if not inserted:
        new_data[week_key] = {day: [lesson.to_dict() for lesson in lessons] for day, lessons in schedule.items()}

    return new_data
