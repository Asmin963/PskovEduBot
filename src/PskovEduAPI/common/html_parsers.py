from bs4 import BeautifulSoup as bs

from src.PskovEduAPI.models import Subject, GradesReport, Student


def html_to_grades(html_content) -> GradesReport:
    """
    Анализирует HTML-код и извлекает оценки для предметов.

    :param html_content: HTML код

    :return: obj `GradesReport`
    """
    soup = bs(html_content, 'html.parser')
    subjects = []

    rows = soup.select('tr[class^="row"]')

    for row in rows[4:]:
        columns = row.find_all('td')
        if len(columns) < 8:
            continue
        name = columns[1].text.strip()
        grades = [int(x) for x in columns[2].text.split(', ') if x.isdigit()]
        avg_grade = float(columns[3].text.strip()) if columns[3].text.strip().isdigit() else 0
        absences = int(columns[4].text.strip())
        skips = int(columns[5].text.strip())
        illnesses = int(columns[6].text.strip())
        latenesses = int(columns[7].text.strip())

        subject = Subject(name, grades, avg_grade, absences, skips, illnesses, latenesses)
        subjects.append(subject)

    return GradesReport(subjects)


def extract_student(html_content) -> Student:
    """
    Извлекает информацию об ученике из HTML

    :param html_content: HTML

    :return: obj `Student`
    """
    soup = bs(html_content, 'html.parser')

    student_div = soup.find('div', class_='one-participant').get_text(strip=True)
    guid = soup.find('div', id='participant')['data-guid']

    parts = student_div.split(',')
    name = parts[0].strip()
    class_name = parts[1].strip()
    school = parts[2].strip()

    return Student(name, class_name, school, guid)