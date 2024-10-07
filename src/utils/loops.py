import time
from threading import Thread

from src.config import cfg
from src.utils import marks_updater

import logging

logger = logging.getLogger(F"Utils{__name__}")


def check_new_marks(acc, bot, delay):
    while True:
        old_marks, new_marks = marks_updater.get_new_marks(acc)
        if new_marks:
            for subject, new_grades in new_marks:
                grades_str = ", ".join(list(map(str, new_grades)))
                old_subject = next((s for s in old_marks.subjects if s.name == subject.name), None)
                message_text = f"🚀 <b>Выставлены новые оценки!\n\n - {subject.name}:</b> <code>{grades_str}</code>\n"
                if old_subject:
                    old_grds = old_subject.grades
                    old_avg = round(sum(old_grds) / len(old_grds), 2) if old_grds else 0
                    message_text += (f"\n<i>Cредний балл: </i><code>{old_avg} -> "
                                     f"{round(sum(subject.grades) / len(subject.grades), 2) if subject.grades else 0}</code>")
                else:
                    message_text += f"\n<i>Cредний балл: </i><code>{subject.avg_grade}</code>"
                logger.info(f'$BRIGHT$CYANНовые оценки: $YELLOW{grades_str}')
                bot.send_message(cfg.owner_id, message_text, parse_mode='HTML')
        time.sleep(delay)

def start_checking_marks(acc, bot, delay=30):
    Thread(target=check_new_marks, args=(acc, bot, delay,), daemon=True).start()
