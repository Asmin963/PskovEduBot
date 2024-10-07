from datetime import timedelta, datetime

def get_monday_date(format="%d.%m.%Y", time=None) -> str | datetime:
    """
    Возвращает дату понедельника текущей недели в формате "dd.mm.yyyy".

    :param format: Формат времени. Если None, то возвращется datetime
    :param time: Время от которого считать текущую неделю. Опционально

    """
    today = time or datetime.today()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime(format) if format else monday