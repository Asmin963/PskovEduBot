from typing import List, Optional, Dict, Any


class Subject:
    """
    Класс, представляющий школьний предмет

    :param name: Название предмета
    :param grades: Список оценок
    :param avg_grade: Средний балл
    :param absences: Количество пропусков
    :param skips: Количество пропущенных уроков
    :param illnesses: Количество болезни
    :param latenesses: Количество пропущенных занятий
    """
    def __init__(self, name, grades, avg_grade, absences, skips, illnesses, latenesses):
        self.name = name
        self.grades = grades
        self.avg_grade = avg_grade
        self.absences = absences
        self.skips = skips
        self.illnesses = illnesses
        self.latenesses = latenesses

    def to_dict(self):
        return {
            "name": self.name,
            "grades": self.grades,
            "avg_grade": self.avg_grade,
            "absences": self.absences,
            "skips": self.skips,
            "illnesses": self.illnesses,
            "latenesses": self.latenesses
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class GradesReport:
    """
    Класс, представляющий отчёт об успеваемости ученика
    """

    def __init__(self, subjects: List[Subject]):
        self.subjects = subjects

    def to_dict(self):
        return {
            "subjects": [subject.to_dict() for subject in self.subjects]
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return cls([])
        subjects = [Subject.from_dict(subject) for subject in data['subjects']]
        return cls(subjects)

    def to_bot_string(self):
        return "<b>🤓 Успеваемость</b>\n\n" + '\n'.join(
            [f"<b>{subject.name}</b>: {", ".join(list(map(str, subject.grades)))}" for subject in self.subjects])


class Student:
    """
    Класс представляющий ученика

    :param name: Имя ученика в формате "Петров И. О."
    :param class_name: Название класса в формате "10У"
    :param school: Полное название школы
    :param guid: Идентификатор ученика
    """

    def __init__(self, name, class_name, school, guid):
        self.name = name
        self.class_name = class_name
        self.school = school
        self.guid = guid

    def to_dict(self):
        return {
            "name": self.name,
            "class_name": self.class_name,
            "school": self.school,
            "guid": self.guid
        }

    def to_bot_string(self):
        return f"""
<b>ℹ️ Информация об ученике</b>

• ФИО: <code>{self.name}</code>
• Школа: <code>{self.school}</code>
• Класс: <code>{self.class_name}</code>"""

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['name'],
            data['class_name'],
            data['school'],
            data['guid']
        )


class Homework:
    def __init__(self, date: str, homework: str, items: list):
        self.date = date
        self.homework = homework
        self.items = items

    def to_dict(self):
        return {
            "date": self.date,
            "homework": self.homework,
            "homeworkItems": self.items
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("date"),
            data.get('homework'),
            data.get('homeworkItems', [])
        )


class Lesson:
    """
    Класс, представляющий урок.

    :param participantGuid: Идентификатор ученика (str)
    :param scheduleItemGuid: Идентификатор расписания урока (str)
    :param journalGuid: Идентификатор журнала урока (str)
    :param lessonTimeGuid: Идентификатор времени урока (str)
    :param subjectGuid: Идентификатор предмета (str)
    :param subject: Название предмета (str)
    :param teacherGuid: Идентификатор учителя (str)
    :param teacher: ФИО учителя (str)
    :param date: Дата урока (str)
    :param lesson_number: Номер урока (str)
    :param lessonTime: Время урока (str)
    :param homework: Домашнее задание (str)
    :param previous_homework: Предыдущее домашнее задание (dict)
    :param topic: Тема урока (str)
    """

    def __init__(self, participantGuid: str, scheduleItemGuid: str, journalGuid: str,
                 lessonTimeGuid: str, subjectGuid: str, subject: str, teacherGuid: str,
                 teacher: str, date: str, lessonNumber: str, lessonTime: str,
                 homework: Optional[str], previousHomework: Optional[Homework], topic: Optional[str],
                 cabinetGuid: Optional[str], cabinet: Optional[str], gradeTypeGuid: Optional[str],
                 gradeType: Optional[str], marks: Optional[list], marksRaw: Optional[list],
                 lessonTimeBegin: Optional[str], lessonTimeEnd: Optional[str], homeworkItems: Optional[list],
                 absence: Optional[list], absenceRaw: Optional[list], notes: Optional[list],
                 periodMark: Optional[bool], weight: Optional[int], gradeHeadComment: Optional[str],
                 markGradeTypes: Optional[list], markCriteria: Optional[list], lateTime: Optional[str],
                 workNames: Optional[list], externalResources: Optional[list], **kwargs):
        self.participantGuid = participantGuid
        self.scheduleItemGuid = scheduleItemGuid
        self.journalGuid = journalGuid
        self.lessonTimeGuid = lessonTimeGuid
        self.subjectGuid = subjectGuid
        self.subject = subject
        self.teacherGuid = teacherGuid
        self.teacher = teacher
        self.date = date
        self.lessonNumber = lessonNumber
        self.lessonTime = lessonTime
        self.homework = homework
        self.previousHomework = previousHomework
        self.topic = topic
        self.cabinetGuid = cabinetGuid
        self.cabinet = cabinet
        self.gradeTypeGuid = gradeTypeGuid
        self.gradeType = gradeType
        self.marks = marks
        self.marksRaw = marksRaw
        self.lessonTimeBegin = lessonTimeBegin
        self.lessonTimeEnd = lessonTimeEnd
        self.homeworkItems = homeworkItems
        self.absence = absence
        self.absenceRaw = absenceRaw
        self.notes = notes
        self.periodMark = periodMark
        self.weight = weight
        self.gradeHeadComment = gradeHeadComment
        self.markGradeTypes = markGradeTypes
        self.markCriteria = markCriteria
        self.lateTime = lateTime
        self.workNames = workNames
        self.externalResources = externalResources

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        homework = Homework.from_dict(data.pop('previousHomework', {}))
        return cls(
            participantGuid=data.get('participantGuid'),
            scheduleItemGuid=data.get('scheduleItemGuid'),
            journalGuid=data.get('journalGuid'),
            lessonTimeGuid=data.get('lessonTimeGuid'),
            subjectGuid=data.get('subjectGuid'),
            subject=data.get('subject'),
            teacherGuid=data.get('teacherGuid'),
            teacher=data.get('teacher'),
            date=data.get('date'),
            lessonNumber=data.get('lessonNumber'),
            lessonTime=data.get('lessonTime'),
            homework=data.get('homework'),
            previousHomework=homework,
            topic=data.get('topic'),
            cabinetGuid=data.get('cabinetGuid'),
            cabinet=data.get('cabinet'),
            gradeTypeGuid=data.get('gradeTypeGuid'),
            gradeType=data.get('gradeType'),
            marks=data.get('marks', []),
            marksRaw=data.get('marksRaw', []),
            lessonTimeBegin=data.get('lessonTimeBegin'),
            lessonTimeEnd=data.get('lessonTimeEnd'),
            homeworkItems=data.get('homeworkItems', []),
            absence=data.get('absence', []),
            absenceRaw=data.get('absenceRaw', []),
            notes=data.get('notes', []),
            periodMark=data.get('periodMark'),
            weight=data.get('weight'),
            gradeHeadComment=data.get('gradeHeadComment'),
            markGradeTypes=data.get('markGradeTypes', []),
            markCriteria=data.get('markCriteria', []),
            lateTime=data.get('lateTime'),
            workNames=data.get('workNames', []),
            externalResources=data.get('externalResources', [])
        )

    def to_dict(self):
        return {
            "previousHomework": hm.to_dict() if (hm := self.__dict__.pop('previousHomework')) else None,
            **{k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        }


class Trimester:
    """
    Класс, описывающий триместр

    :param schoolEduPeriodGuid: Идентификатор учебного периода в школе (str)
    :param eduPeriodGuid: Идентификатор учебного периода (str)
    :param parentEduPeriodGuid: Идентификатор родительского учебного периода (str)
    :param name: Название учебного периода (str)
    :param dateBegin: Дата начала учебного периода (str)
    :param dateEnd: Дата окончания учебного периода (str)
    """

    def __init__(self, schoolEduPeriodGuid, eduPeriodGuid, parentEduPeriodGuid, name, dateBegin, dateEnd):
        self.school_edu_periodGuid = schoolEduPeriodGuid
        self.edu_periodGuid = eduPeriodGuid
        self.parent_edu_periodGuid = parentEduPeriodGuid
        self.name = name
        self.date_begin = dateBegin
        self.date_end = dateEnd

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return {
            "schoolEduPeriodGuid": self.school_edu_periodGuid,
            "eduPeriodGuid": self.edu_periodGuid,
            "parentEduPeriodGuid": self.parent_edu_periodGuid,
            "name": self.name,
            "dateBegin": self.date_begin,
            "dateEnd": self.date_end
        }


class Diary:
    """
    Класс, описывающий дневник ученика

    :param date: Дата дневника (str)
    :param days: Словарь уроков по дням (dict)
    :param edu_periods: Список учебных периодов (List[Trimester])
    """

    def __init__(self, date: str, days: Dict[str, List[Lesson]], edu_periods: List[Trimester]):
        self.date = date
        self.days = days
        self.edu_periods = edu_periods

    @classmethod
    def from_dict(cls, data):
        date = data.pop("date", None)
        lessons = {k: [Lesson.from_dict(r) for r in v] for k, v in data['diary'].items()} if data['diary'] else {}
        edu_periods = [Trimester(**v) for v in data['edu_periods']]
        return cls(date, lessons, edu_periods)

    def to_dict(self, no_periods=False):
        d = {
            "date": self.date,
        }
        for k, v in self.days.items():
            d[k] = [l.to_dict() for l in v]
        if not no_periods:
            d['edu_periods'] = [p.to_dict() for p in self.edu_periods]
        return d





class Event:
    """
    Класс, описывающий событие

    :param sys_guid: Идентификатор события
    :param sys_guidfk: Внешний идентификатор события
    :param sys_state: Состояние события
    :param sys_fldorder: Порядок поля
    :param sys_rev: Ревизия события
    :param sys_parentguid: Идентификатор родительского события
    :param sys_user: Пользователь, связанный с событием
    :param sys_creator: Создатель события
    :param sys_created: Дата и время создания события
    :param sys_updated: Дата и время обновления события
    :param title: Название события
    :param message: Сообщение события. Может содержать текст или html-код сообщения
    :param type: Тип события
    :param time_begin: Время начала события
    :param time_end: Время окончания события
    :param duration: Продолжительность события
    """

    def __init__(self, sys_guid: str, sys_guidfk: Optional[str], sys_state: str, sys_fldorder: Optional[str],
                 sys_rev: str,
                 sys_parentguid: Optional[str], sys_user: str, sys_creator: str, sys_created: str, sys_updated: str,
                 title: str,
                 message: str, type: str, time_begin: str, time_end: str, duration: str):
        self.sys_guid = sys_guid
        self.sys_guidfk = sys_guidfk
        self.sys_state = sys_state
        self.sys_fldorder = sys_fldorder
        self.sys_rev = sys_rev
        self.sys_parentguid = sys_parentguid
        self.sys_user = sys_user
        self.sys_creator = sys_creator
        self.sys_created = sys_created
        self.sys_updated = sys_updated
        self.title = title
        self.message = message
        self.type = type
        self.time_begin = time_begin
        self.time_end = time_end
        self.duration = duration

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_dict(self):
        return {
            **{k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        }
