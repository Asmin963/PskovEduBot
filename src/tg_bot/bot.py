import logging
import time
from threading import Thread
from typing import Callable, List

from telebot import TeleBot, types
from telebot.types import CallbackQuery, Message, InlineQuery, BotCommand, User

from src.PskovEduAPI import Client
from src.config import cfg
from src.tg_bot.handlers.grades import init_handlers
from src.tg_bot.handlers.inline import init_inline_handlers

from colorama import Style

logger = logging.getLogger("Bot")


class TgBot(TeleBot):
    """
    Класс для бота, наследованный от TeleBot, включающий вспомогательные функции
    """

    def __init__(self, token: str, **kwargs):
        self.tg = kwargs.pop('tg', None)
        self._original_send_message = self.send_message
        self.send_message = self.smart_send
        super().__init__(token=token, **kwargs)

    def smart_send(self,
                   chat_id: int | List[int],
                   text: str,
                   reply_markup: types.InlineKeyboardMarkup = None,
                   parse_mode: str = None,
                   get_msgs_list: bool = False,
                   _raise: bool = False,
                   clear_state: dict = None,
                   **kwargs
                   ) -> Message | List[Message]:
        """
        Умная отправка сообщения

        :param chat_id: ID чата. Может быть списком ID
        :param text: Текст сообщения
        :param reply_markup: Клавиатура
        :param parse_mode: Форматирование. HTML или Markdown
        :param get_msgs_list: Получать список сообщений, если отправка в несколько чатов?
        :param _raise: Возбуждать исключение в случае ошибки?
        :param clear_state: очищать состояние пользователя?
        :param kwargs: Доп. аргументы

        :return: Сообщение или список собщений
        """
        try:
            if isinstance(chat_id, list):
                messages = []
                for i in chat_id:
                    msgs = self._send_message_in_parts(chat_id=i, text=text, reply_markup=reply_markup,
                                                       parse_mode=parse_mode, **kwargs)
                    if get_msgs_list:
                        messages.extend(msgs)

                result = messages or None
            else:
                result = self._send_message_in_parts(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                     parse_mode=parse_mode, **kwargs)

            if clear_state and self.tg:
                self.tg.clear_st(clear_state.get('chat_id'), clear_state.get("user_id"), clear_state.get("del_msg"))

            return result
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            logger.debug(f"Не смог отправить собщение: \n{text}")
            logger.debug("TRACEBACK", exc_info=True)
            if _raise:
                raise e

    def _send_message_in_parts(self, chat_id, text, reply_markup=None, parse_mode=None, **kwargs):
        max_length = 4096
        messages = []
        while len(text) > max_length:
            part = text[:max_length]
            text = text[max_length:]
            m = self._original_send_message(chat_id=chat_id, text=part, parse_mode=parse_mode, **kwargs)
            messages.append(m)

        m = self._original_send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode,
                                        **kwargs)
        messages.append(m)

        return messages if len(messages) > 1 else messages[0]

    def edit_message(self, message: types.Message, text: str = None, reply_markup=None, _raise=False,
                     **kwargs) -> types.Message:
        """
        Изменяет сообщение

        :param message: сообщение obj`Message`
        :param text: Текст сообщения. Опционально
        :param reply_markup: Клавиатура. Опционально
        :param _raise: Возбуждать исключение в случае ошибки?
        :param kwargs: Доп. агрументы

        :return: Сообщение obj`Message`
        """
        if not text and not reply_markup and not kwargs:
            return
        try:
            if not text and not reply_markup:
                return self.edit_message_text(message.text, message.chat.id, message.id,
                                              reply_markup=message.reply_markup, **kwargs)
            if not text:
                return self.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id,
                                                      reply_markup=reply_markup, **kwargs)
            return self.edit_message_text(text, message.chat.id, message.id, reply_markup=reply_markup, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при изменении сообщения - {str(e)}")
            logger.debug("TRACEBACK", exc_info=True)
            if _raise:
                raise e

    def del_msg(self, message: types.Message | int, chat_id=None, _raise=False, **kwargs):
        """
        Удаляет сообщение

        :param message: сообщение obj`Message`
        :param chat_id: ChatID. Опционально. Передается только в случае, если в message - ID сообщения, а не obj`Message`
        :param _raise: Возбуждать исключение в случае ошибки?
        :param kwargs: Доп. аргументы
        """
        try:
            if isinstance(message, types.Message) or not chat_id:
                return self.delete_message(message.chat.id,
                                           message.id, **kwargs)
            else:
                return self.delete_message(message, chat_id, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения - {str(e)}")
            logger.debug("TRACEBACK", exc_info=True)
            if _raise:
                raise e

    def answer_cb(self, c: types.CallbackQuery, text: str = None, show_alert=False, _raise=False, **kwargs):
        """
        Отвечает на callback-кнопку

        :param c: CallbackQuery
        :param text: Текст ответа
        :param show_alert: True, если нужно показать уведомление, False - если нет
        :param _raise: True, если нужно выбросить исключение при ошибке
        :param kwargs: Дополнительные аргументы
        """
        try:
            return self.answer_callback_query(c.id, text, show_alert=show_alert, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при ответе на callback - {str(e)}")
            logger.debug("TRACEBACK", exc_info=True)
            if _raise:
                raise e


class Telegram:
    def __init__(self, token: str, client: Client):
        self.token = token
        self.client = client

        self.bot: TeleBot = None
        self.bot_me: User = None

        self.commands = {
            "start": "Начать работу",
            "profile": "Профиль текущего ученика",
            "grades": "Получить оценки",
            "settings": "Настройки",
            "homework": "Домашнее задание"
        }

        self._states = {}

        self.no_admin_messages = {}

    def add_func(self, f, kwargs, key='func'):
        existing_func = kwargs.get(key)
        if existing_func:
            kwargs[key] = lambda m: existing_func(m) and f(m)
        else:
            kwargs[key] = f

    def apply_common_filters(self, text=None, state=None, chats=None, commands=None, **kwargs):
        if text:
            kwargs['regexp'] = fr"^{text}$"
        if state:
            self.add_func(lambda m: self.check_st(m.chat.id, m.from_user.id, state), kwargs)
        if chats:
            self.add_func(lambda m: m.chat.id in chats, kwargs)
        if commands:
            kwargs['commands'] = commands
        return kwargs

    def msg_handler(self, handler: Callable, only_txt: bool = False, text: str = None, state: str = None,
                    commands: list = None,
                    chats: List[int] = None, **kwargs):
        """
        Регистрирует хэндлер, срабатывающий при новом сообщении.

        :param handler: хэндлер.
        :param only_txt: только текстовые сообщения.
        :param text: конкретное текстовое значение.
        :param state: состояние пользователя для хендлера.
        :param commands: список команд, для которых срабатывает хендлер.
        :param chats: список ID чатов, для которых срабатывает хендлер.
        :param kwargs: аргументы для хендлера.
        """

        if only_txt or text:
            kwargs['content_types'] = ['text']

        kwargs = self.apply_common_filters(text=text, state=state, chats=chats, commands=commands, **kwargs)

        @self.bot.message_handler(**kwargs)
        def run_msg_handler(message: Message):
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Ошибка при выполнении хендлера тг-бота - {e}")
                logger.debug("TRACEBACK", exc_info=True)

    def cbq_handler(self, handler: Callable, func=None):
        """
        Регистрирует хэндлер, срабатывающий при новом callback'е.

        :param handler: хэндлер.
        :param func: функция-фильтр.
        """
        kwargs = {}
        kwargs['func'] = func or (lambda c: True)

        @self.bot.callback_query_handler(**kwargs)
        def run_handler(call: CallbackQuery):
            try:
                handler(call)
            except Exception as e:
                logger.error(f"Ошибка при выполнении хендлера тг-бота - {e}")
                logger.debug("TRACEBACK", exc_info=True)

    def register_inline_handler(self, function, func=None):
        """
        Регистрирует Инлайн обработчик
        :param function: функция хендлер
        :param func: функция-фильтр
        :return:
        """
        if not func:
            func = lambda q: True

        @self.bot.inline_handler(func)
        def run_inline_handler(q: InlineQuery):
            try:
                function(q)
            except Exception as e:
                logger.error(f"Ошибка при выполнении инлайн хендлера тг-бота - {e}")
                logger.debug("TRACEBACK", exc_info=True)

    def check_st(self, chat_id: int, user_id: int, state: str | list | tuple) -> bool:
        """
        Проверяет, является ли состояние указанным.

        :param chat_id: id чата.
        :param user_id: id пользователя.
        :param state: состояние.

        :return: True / False
        """
        try:
            if isinstance(state, str):
                return self._states[chat_id][user_id]["state"] == state
            cur_st = self._states[chat_id][user_id]["state"]
            return cur_st in state
        except KeyError:
            return False

    def clear_st(self, chat_id: int, user_id: int, del_msg: bool = False) -> int | None:
        """
        Очищает состояние пользователя.

        :param chat_id: id чата.
        :param user_id: id пользователя.
        :param del_msg: удалять ли сообщение, после которого было обозначено текущее состояние.

        :return: ID сообщения-инициатора или None, если состояние и так было пустое.
        """
        try:
            state = self._states[chat_id][user_id]
        except KeyError:
            return None

        msg_id = state.get("mid")
        del self._states[chat_id][user_id]
        if del_msg:
            try:
                self.bot.delete_message(chat_id, msg_id)
            except:
                pass
        return msg_id

    def set_st(self, chat_id: int, user_id: int, message_id: int, state: str, data: dict | None = None):
        """
        Устанавливает состояние для пользователя.

        :param chat_id: id чата.
        :param message_id: id сообщения, после которого устанавливается данное состояние.
        :param user_id: id пользователя.
        :param state: состояние.
        :param data: доп. данные.
        """
        if chat_id in self._states:
            try:
                self.bot.delete_message(chat_id, self._states[chat_id][user_id]['mid'])
            except:
                ...
        if chat_id not in self._states:
            self._states[chat_id] = {}
        self._states[chat_id][user_id] = {"state": state, "mid": message_id, "data": data or {}}

    def get_state_data(self, chat_id: int, user_id: int) -> dict | None:
        """
        Получает данные состояния пользователя

        :param chat_id: ID чата
        :param user_id: ID пользователя

        :return: dict | None
        """
        try:
            return self._states[chat_id][user_id]['data']
        except KeyError:
            return None

    def get_state(self, chat_id: int, user_id: int) -> dict | None:
        """
        Получает состояние пользователя

        :param chat_id: ID чата
        :param user_id: ID пользователя

        :return: dict | None
        """
        try:
            return self._states[chat_id][user_id]
        except KeyError:
            return None

    def set_commands(self):
        """
        Устанавливает команды
        """
        self.bot.set_my_commands([
            BotCommand(command, description) for command, description in self.commands.items()
        ])

    def set_short_description(self):
        """
        Устанавливает описание бота
        """
        text = "📚 Бот для упрощения работы с one.pskovedu.ru"
        if cfg.github_url:
            text += f"\n\n🧑🏻‍💻 Github - {cfg.github_url}"
        self.bot.set_my_short_description(text)

    def set_description(self):
        desc = f"""
🤖 Бот для работы с Псковским образовательным порталом one.pskovedu.ru

🔔 Уведомления
👩‍🏫 Данные об учителях
💡 Инлайн-режим
🎒 Расписания уроков
"""
        if cfg.github_url:
            desc += f"\n🖥 Github - {cfg.github_url}"
        self.bot.set_my_description(desc)

    def register_admin_hanlder(self, m: Message):
        cfg.set("owner_id", m.from_user.id)
        self.bot.send_message(m.chat.id, f"🚀 <b>Нажми /start</b>")

    def init(self):
        """
        Инициализация бота.
        """
        self.bot = TgBot(token=self.token, parse_mode='HTML')
        self.bot_me = self.bot.get_me()

        self.msg_handler(self.register_admin_hanlder, func=lambda _: not cfg.owner_id)

        self.set_description()
        self.set_short_description()
        self.set_commands()

        init_handlers(self)
        init_inline_handlers(self)

        return self

    def start(self, error_delay: int = 60):
        """
        Запускает поллинг
        """

        def run():
            while True:
                try:
                    self.bot.infinity_polling(timeout=60)
                except Exception as e:
                    logger.error(f"Ошибка при запуске тг-бота - {e}")
                    logger.debug("TRACEBACK", exc_info=True)
                    time.sleep(error_delay)

        Thread(target=run).start()
        logger.info(f"{Style.BRIGHT}$CYANTelegram-бот $YELLOWt.me/{self.bot_me.username}$CYAN запущен")
