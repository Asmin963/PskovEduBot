import telebot.types
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

from ..config import cfg

from . import CBT

def settings_kb():
    """
    Клавиатура из меню настроек
    """
    params = [
        (cfg.new_graders_notification, "Уведомления о новых оценках", "new_graders_notification"),
        (cfg.inline_mode, "Инлайн-режим", "inline_mode"),
        (cfg.show_name_in_inline, "Показывать ФИО в инлайн режиме", "show_name_in_inline")
    ]
    return K(row_width=1).add(*[
        B(f"{'🟢' if param else '🔴'} {description}", None, f'{CBT.TOGGLE_SETTINGS}:{callback}')
        for param, description, callback in params
    ])

def inline_share(query=""):
    """
    Кнопка поделиться при инлайн запросе
    """
    return K().add(
        B("🪄 Поделиться", switch_inline_query_chosen_chat=telebot.types.SwitchInlineQueryChosenChat(
            query,
            allow_group_chats=True,
            allow_user_chats=True,
        ))
    )

def github(text='👨🏼‍💻 Github'):
    """
    Клавиатура возвращающая ссылку на репозиторий проекта
    """
    return K().add(B(text, cfg.github_url)) if cfg.github_url else None

def get_homework_menu(weeks_indent=0):
    """
    Получает клавиатуру меню получения домашнего задания

    :param weeks_indent: отступ в неделях
    """
    kb = K(row_width=1).add(
        B("Понедельник", None, f"{CBT.GET_HOMEWORK}:1:1:{weeks_indent}"),
        B("Вторник", None, f"{CBT.GET_HOMEWORK}:2:1:{weeks_indent}"),
        B("Среда", None, f"{CBT.GET_HOMEWORK}:3:1:{weeks_indent}"),
        B("Четверг", None, f"{CBT.GET_HOMEWORK}:4:1:{weeks_indent}"),
        B("Пятница", None, f"{CBT.GET_HOMEWORK}:5:1:{weeks_indent}"),
    )
    kb.row(
        B("⬅️", None, f'{CBT.GET_HOMEWORK_MENU}:{weeks_indent - 1}'),
        B("➡️️", None, f'{CBT.GET_HOMEWORK_MENU}:{weeks_indent + 1}'),
    )
    return kb

def back_to_homework_menu(indent=0):
    return K().add(B("⬅️ Назад", None, f"{CBT.GET_HOMEWORK_MENU}:{indent}"))

def star_it():
    return K().add(
        B("⭐️ Оценить проект", "https://github.com/Asmin963/PskovEduBot?tab=readme-ov-file#-поддержите-проект")
    )