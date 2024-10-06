import datetime

from telebot.types import Message, CallbackQuery

from ...config import cfg
from ...utils import me_loader, scheluder, tools
from .. import keyboards as kbs, CBT


def init_handlers(tg):
    bot = tg.bot

    def start_handler(m: Message):
        bot.send_message(m.chat.id, "👋 <b>Привет! Я бот для работы с one.pskovedu.ru\n\n"
                                    "🔔 Я могу уведомлять о новых оценках!</b>", reply_markup=kbs.github())

    def not_admin_handler(m: Message):
        if m.chat.id in tg.no_admin_messages:
            bot.del_msg(tg.no_admin_messages[m.chat.id])
        result = bot.send_message(m.chat.id, "👑 <b>Команда доступна только для владельца бота.</b>",
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
            scheluder.save_diary_to_schedule(diary)
        except:
            return bot.answer_cb(c.id, "На эту дату домашки нет")
        lessons = list(diary.days.values())[day - 1]

        homework_str = ""
        for lesson in lessons:
            if lesson.homework:
                homework_str += f"<b>{lesson.subject}</b>\n"
                homework_str += f"<i>{lesson.homework}</i>\n\n"

        if not edit:
            bot.send_message(c.message.chat.id, homework_str)
            bot.answer_cb(c)
        else:
            bot.edit_message(c.message, homework_str, kbs.back_to_homework_menu(indent))

    def homework_menu_cb(c: CallbackQuery, weeks_indent=0):
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
        bot.edit_message(c.message, f"<b>({weekdays[0].strftime("%d.%m.%Y")} - {weekdays[-1].strftime("%d.%m.%Y")})\nВыбери день недели: </b>",
                         kbs.get_homework_menu(weeks_indent))

    def homework_menu(m: Message):
        weekdays = tools.weekdays()
        bot.send_message(m.chat.id,
                         f"<b>({weekdays[0].strftime("%d.%m.%Y")} - {weekdays[-1].strftime("%d.%m.%Y")})\nВыбери день недели: </b>",
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
