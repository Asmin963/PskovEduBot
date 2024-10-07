import json
import sys
import time

from colorama import Fore, Style
from telebot import TeleBot

default_config = {
    "token": "",
    "phpsessid": "",
    "owner_id": 0,
    "x1sso": None,
    "delay": 10,
    "new_graders_notification": True,
    "inline_mode": True,
    "show_name_in_inline": False
}


def create_config_obj(settings: dict) -> dict:
    """
    Создает объект конфига с нужными настройками.

    :param settings: dict настроек.
    :return: объект конфига.
    """
    config = settings.copy()
    return config


def save_config(config: dict, path: str = "storage/cfg.json"):
    """
    Сохраняет конфиг в формате JSON в указанный путь.

    :param config: dict настроек.
    :param path: путь к файлу для сохранения.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def first_setup():
    config = create_config_obj(default_config)
    sleep_time = 1

    print(f"{Fore.CYAN}{Style.BRIGHT}Привет! {Fore.RED}(`-`)/{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Не могу найти основной конфиг... {Fore.RED}(-_-;). . .{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Давай проведем первичную настройку! {Fore.RED}°++°{Style.RESET_ALL}")
    time.sleep(sleep_time)

    while True:
        try:
            print(
                f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Введи API-токен Telegram-бота (получить его можно у @BotFather). "
                f"{Fore.RED}(._.){Style.RESET_ALL}")
            token = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
            if not (token and token.split(":")[0].isdigit()):
                raise Exception()
            if TeleBot(token).get_me().username is None:
                raise Exception()
            config["token"] = token
            break
        except:
            print(
                f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат токена. Попробуй еще раз! {Fore.RED}\(!!˚0˚)/{Style.RESET_ALL}")

    while True:
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Введи свой PHPSESSID для доступа к порталу one.pskovedu.ru (Используй Расширение EditThisCookie)"
            f" {Fore.RED}(._.){Style.RESET_ALL}")
        phpsessid = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if len(phpsessid) == 32:
            config["phpsessid"] = phpsessid
            break
        else:
            print(
                f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат PHPSESSID. Попробуй еще раз! {Fore.RED}(°_o){Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Готово! Сейчас я сохраню конфиг и завершу программу! "
          f"{Fore.RED}ʘ>ʘ{Style.RESET_ALL}")
    save_config(config)

    print(f"{Fore.CYAN}{Style.BRIGHT}Запусти меня снова и напиши своему Telegram-боту. "
          f"Все остальное ты сможешь настроить через него. {Fore.RED}ʕ•ᴥ•ʔ{Style.RESET_ALL}")
    time.sleep(10)
    sys.exit()
