import json
import os

from src.PskovEduAPI import models
from src.PskovEduAPI.models import GradesReport

FILEPATH = os.path.join(os.path.abspath(os.path.dirname(__name__)), "storage", "user.json")


def _format_data(data: dict):
    if "grades" not in data and "subjects" in data:
        (new_dict := {})["grades"] = data
        return new_dict
    if "user" not in data and any("класс" in key for key in list(data.keys())):
        (new_dict := {})["user"] = data
        return new_dict

    return data


def _save(data):
    data = _format_data(data)
    with open(FILEPATH, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return data


def _load():
    if not os.path.exists(FILEPATH):
        return {}

    with open(FILEPATH, 'r', encoding="utf-8") as file:
        return _format_data(json.load(file))


def load_grades():
    data = _load()
    return GradesReport.from_dict(data.get('grades'))


def save_grades(marks_report: models.GradesReport):
    data = _load()
    data['grades'] = marks_report.to_dict()
    return _save(data)


def load_me():
    data = _load()
    return models.Student.from_dict(data.get("user")) if data.get("user") else None


def save_me(user: models.Student):
    data = _load()
    data['user'] = user.to_dict()
    return _save(data)
