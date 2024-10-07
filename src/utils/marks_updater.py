import traceback
from typing import List, Tuple

from src import PskovEduAPI
from src.PskovEduAPI import models
from src.utils import me_loader

import logging

logger = logging.getLogger(f"Utils.{__name__}")


def compare_and_update(old_marks_report, new_marks_report) -> List[Tuple[models.Subject, List[int]]]:
    """
    Выводит новые оценки из новых данных, сравнивая со старыми
    """
    updated = []

    old_dict = {s.name: s for s in old_marks_report.subjects}
    new_dict = {s.name: s for s in new_marks_report.subjects}

    for name, new in new_dict.items():
        old_subject = old_dict.get(name)

        if not old_subject:
            new_grades = new.grades
        else:
            new_grades = new.grades[len(old_subject.grades):] if len(new.grades) > len(
                old_subject.grades) else []

        if new_grades:
            updated.append((new, new_grades))

    return updated


def get_new_marks(client: PskovEduAPI.Client):
    try:
        new_grades = client.get_grades_report(1)
        old_ws = me_loader.load_grades()

        if not old_ws:
            me_loader.save_grades(new_grades)
            return None, None

        new_ws = compare_and_update(old_ws, new_grades)
        me_loader.save_grades(new_grades)

        if new_ws:
            return old_ws, new_ws
        return None, None
    except Exception as e:
        logger.error(f"Ошибка при получении новых оценок: {str(e)}")
        logger.error("TRACEBACK", exc_info=True)
        return None, None

