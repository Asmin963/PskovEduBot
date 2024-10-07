from datetime import datetime

from ...config import cfg
from ...utils import me_loader

from telebot.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from .. import keyboards as kbs


def init_inline_handlers(tg):
    bot = tg.bot

    def main_inline_handler(q: InlineQuery):
        marks = me_loader.load_grades() if q.from_user.id == cfg.owner_id and cfg.inline_mode else None

        results = []

        if cfg.github_url:
            text = f"🎓 <b>Telegram Bot для взаимодействия с образовательным порталом one.pskovedu.ru</b>\n\n"
            text += f"<b>🧑🏻‍💻 Разработчик - <a href='https://t.me/arthells'></a>@arthells</b>\n"
            text += f"<b>🔗 Ссылка на <a href='{cfg.github_url}'>Github</a></b>\n\n"
            github_result = InlineQueryResultArticle(
                id=52525252525252,
                title="👨🏼‍💻 Information",
                description="Информация о проекте",
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML"
                ),
                reply_markup=kbs.github("🖥 Создать бота"),
                # thumbnail_url="https://avatars.githubusercontent.com/u/80214183?v=4"
            )
            results.append(github_result)


        if marks is not None:
            for i, subject in enumerate(marks.subjects):
                grades_str = ", ".join(list(map(str, subject.grades))) if subject.grades else "Нет оценок"
                avg = subject.avg_grade or (
                    round(sum(subject.grades) / len(subject.grades), 2) if subject.grades else 0)
                result_text = f"<b>📚 {subject.name}</b>\n\nОценки: <code>{grades_str}</code>\nСредний балл: <code>{avg}</code>"

                me = me_loader.load_me() or tg.client.get_me()
                me_loader.save_me(me)

                if cfg.show_name_in_inline:
                    result_text = f"👶 <b><i>Ученик: </i></b><code>{me.name}</code>\n\n{result_text}"
                result = InlineQueryResultArticle(
                    id=i,
                    title=subject.name,
                    description="Оценки: " + grades_str + f"\nСредний балл: {avg}",
                    input_message_content=InputTextMessageContent(
                        message_text=result_text,
                        parse_mode="HTML"
                    ),
                    reply_markup=kbs.github("🖥 Создать бота"),
                    # thumbnail_url="https://static.rustore.ru/apk/1574868927/content/ICON/06ae4f6a-f68c-4ec9-826d-1442d7d4b146.png"
                )
                results.append(result)

        return bot.answer_inline_query(q.id, results, cache_time=0)

    tg.register_inline_handler(main_inline_handler)