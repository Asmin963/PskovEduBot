import os
import sys
from colorama import Fore, Style

from src.utils.loops import start_checking_marks
from src.tg_bot.bot import Telegram
from src.PskovEduAPI import Client
from src.config import cfg
from src.utils import me_loader, tools
from src.utils.tools import create_dirs
from src.utils.logger import LOGGER_CONFIG

import logging.config

os.system('')

create_dirs()

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(f"main")

def main():
    if not os.path.exists("storage/cfg.json"):
        from first_setup import first_setup
        first_setup()

    logger.debug("------------------------------------------------------------------")

    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}By {Fore.BLUE}{Style.BRIGHT}t.me/soxbz{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT} * GitHub: {Fore.BLUE}{Style.BRIGHT}github.com/Asmin963/PskovEduBot{Style.RESET_ALL}\n")

    client = Client(cfg.phpsessid, cfg.x1sso)
    gr = client.get_grades_report()

    tools.start_log(client.me, gr)

    me_loader.save_grades(gr)
    me_loader.save_me(client.me)

    telegram = Telegram(cfg.token, client).init()
    start_checking_marks(client, telegram.bot, delay=cfg.delay)
    telegram.start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Критическая ошибка - {str(e)}")
        logger.debug("TRACEBACK", exc_info=True)
        logger.critical(f"Завершаю программу")
        sys.exit()
