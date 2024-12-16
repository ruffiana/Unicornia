import os
from pathlib import Path
import json
import logging
import time

from . import const


class Guilds:
    try:
        GUILD_IDS = os.getenv("GUILD_IDS")
        if GUILD_IDS:
            GUILD_IDS = [int(x) for x in os.getenv("GUILD_IDS").split(",")]
    except ValueError:
        GUILD_IDS = None

    DATA_FILEPATH = Path(__file__).parent / "data"
    GUILDS_FILEPATH = DATA_FILEPATH / "guilds.json"

    def __init__(self, parent=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.parent = parent

        self.guilds = self._load()

    @property
    def ids(self):
        if not self.guilds:
            return []
        else:
            return [int(id_) for id_ in self.guilds.keys()]

    def add_user(self, guild_id: str, uid: str, user):
        if guild_id not in self.guilds:
            self.logger.info("Adding new guild with GID {}".format(guild_id))
            self.guilds[guild_id] = {}

        if uid not in self.guilds.get(guild_id):
            self.logger.info("Added new user with GID:UID {}:{}".format(guild_id, uid))

        user["last_updated"] = round(time.time())
        self.guilds[guild_id][uid] = user

        self._save()

    def _refresh(self):
        now = round(time.time())
        old = {**self.guilds}

        for guild_id, users in self.guilds.items():
            self.guilds[guild_id] = {
                k: v for k, v in users.items() if v.get("last_updated") >= now - 60
            }

        if self.guilds != old:
            self._save()

    def _load(self):
        if not self.GUILDS_FILEPATH.exists():
            return {}
        try:
            with open(self.GUILDS_FILEPATH, "r") as f:
                data = json.loads(f.read())
                return data
        except (FileNotFoundError, IOError, json.decoder.JSONDecodeError) as err:
            self.logger.debug(f"Error loading {self.GUILDS_FILEPATH}: {err}")
            return {}

    def _save(self):
        try:
            self.DATA_FILEPATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.GUILDS_FILEPATH, "w") as f:
                f.write(json.dumps(self.guilds))
            return True
        except IOError as err:
            self.logger.debug(f"Error saving {self.GUILDS_FILEPATH}: {err}")
            return False
