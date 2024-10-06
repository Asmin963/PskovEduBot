import json
import os


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self.__token: str = None
        self.phpsessid: str = None
        self.owner_id: int = None
        self.x1sso: str = None
        self.delay: int = None

        self.new_graders_notification: bool = None
        self.inline_mode: bool = None
        self.show_name_in_inline: bool = None

        self.github_url: str = "github.com/Asmin963/PskovEduBot"


    def load_config(self):
        if not os.path.exists(self.config_path):
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.__token = data.get("token")
            self.phpsessid = data.get("phpsessid")
            self.owner_id = data.get("owner_id")
            self.x1sso = data.get("x1sso")

            self.delay = data.get("delay")

            self.new_graders_notification = data.get("new_graders_notification")
            self.inline_mode = data.get("inline_mode")
            self.show_name_in_inline = data.get('show_name_in_inline')

            if not self.__token:
                raise ValueError("Токен не найден в конфиге")
            if not self.phpsessid:
                raise ValueError("PHPSESSID не найден в конфиге")

        return self

    def _save(self):
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump({
                "token": self.__token,
                "phpsessid": self.phpsessid,
                "owner_id": self.owner_id,
                "x1sso": self.x1sso,
                "delay": self.delay,

                "new_graders_notification": self.new_graders_notification,
                "inline_mode": self.inline_mode,
                "show_name_in_inline": self.show_name_in_inline
            }, file, indent=4)

    def set(self, key, val):
        setattr(self, key, val)
        self._save()

    def toggle(self, param):
        setattr(self, param, not bool(getattr(self, param)))
        self._save()

    @property
    def token(self):
        return self.__token


cfg = ConfigLoader("../storage/cfg.json").load_config()
