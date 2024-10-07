import datetime

from telebot.types import Message, CallbackQuery

from ...config import cfg
from ...utils import me_loader, scheduler, tools
from .. import keyboards as kbs, CBT


def init_handlers(tg):
    bot = tg.bot

    def start_handler(m: Message):
        text = f"🎓 <b>Telegram Bot для взаимодействия с образовательным порталом one.pskovedu.ru</b>\n\n"
        text += f"<b>🧑🏻‍💻 Разработчик - <a href='https://t.me/arthells'></a>@arthells</b>\n"
        text += f"<b>🔗 Ссылка на <a href='{cfg.github_url}'>Github</a></b>\n\n"
        bot.send_message(m.chat.id, text, reply_markup=kbs.github("📱 Инструкция по установке"))

    def not_admin_handler(m: Message):
        if m.chat.id in tg.no_admin_messages:
            bot.del_msg(tg.no_admin_messages[m.chat.id])
        result = bot.send_message(m.chat.id, "👑 <b>Команда доступна только для владельца</b>",
                                  reply_markup=kbs.github("🛠 Создать своего бота"))
        tg.no_admin_messages[m.chat.id] = result.message_id

    def grades_handler(m: Message):
        bot.send_message(m.chat.id, me_loader.load_grades().to_bot_string(), reply_markup=kbs.inline_share())

    def profile_handler(m: Message):
        bot.send_message(m.chat.id, tg.client.get_me().to_bot_string())

    def settings(m: Message):
        bot.send_message(m.chat.id, "⚙️ <b>Меню настроек</b>", reply_markup=kbs.settings_kb())

    def toggle_settings_param(c: CallbackQuery):
        cfg.toggle(c.data.split(":")[-1])
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=kbs.settings_kb())

    def get_homework(c: CallbackQuery):
        day, edit, indent = list(map(int, c.data.split(":")[1:]))
        try:
            diary = tg.client.fetch_diary(indent=indent)
            scheduler.save_diary_to_schedule(diary)
        except:
            return bot.edit_message(c.message, "🥳 На эту дату домашки нет!", kbs.back_to_homework_menu(indent))
        lessons = list(diary.days.values())[day - 1]

        homework_str = ""
        homework_str += f"📅 <b>{tools.get_weekday(day - 1)}, {lessons[0].date}</b>\n\n"
        for lesson in lessons:
            if lesson.homework:
                homework_str += f"<b>{lesson.subject}</b>\n"
                homework_str += f"<i>{lesson.homework}</i>\n\n"

        if not edit:
            bot.send_message(c.message.chat.id, homework_str)
            bot.answer_cb(c)
        else:
            bot.edit_message(c.message, homework_str, kbs.back_to_homework_menu(indent))

    def homework_menu_cb(c: CallbackQuery):
        split = c.data.split(":")
        if len(split) > 1:
            weeks_indent = int(split[-1])
            td = datetime.timedelta(weeks=abs(weeks_indent))

            if weeks_indent < 0:
                weekdays = tools.weekdays(date=datetime.datetime.now() - td)
            else:
                weekdays = tools.weekdays(date=datetime.datetime.now() + td)
        else:
            weekdays = tools.weekdays()
        bot.edit_message(c.message,
                         f"<b>🎒 {tg.client.me.class_name}\n\n📆 {weekdays[0].strftime("%d.%m.%Y")} - {weekdays[-1].strftime("%d.%m.%Y")}\n"
                         f"\nВыбери день недели: </b>",
                         reply_markup=kbs.get_homework_menu())

    def homework_menu(m: Message):
        weekdays = tools.weekdays()
        bot.send_message(m.chat.id,
                         f"<b>🎒 {tg.client.me.class_name}\n\n📆 {weekdays[0].strftime("%d.%m.%Y")} - {weekdays[-1].strftime("%d.%m.%Y")}\n"
                         f"\nВыбери день недели: </b>",
                         reply_markup=kbs.get_homework_menu())

    tg.msg_handler(start_handler, commands=['start'])
    tg.msg_handler(homework_menu, commands=['homework'])

    tg.cbq_handler(toggle_settings_param, lambda c: c.data.startswith(f'{CBT.TOGGLE_SETTINGS}:'))

    tg.cbq_handler(get_homework, lambda c: c.data.startswith(f'{CBT.GET_HOMEWORK}:'))
    tg.cbq_handler(homework_menu_cb, lambda c: c.data.startswith(f"{CBT.GET_HOMEWORK_MENU}"))

    tg.msg_handler(not_admin_handler, func=lambda m: cfg.owner_id != m.from_user.id)

    tg.msg_handler(profile_handler, commands=['profile'])
    tg.msg_handler(grades_handler, commands=['grades'])
    tg.msg_handler(settings, commands=['settings'])
