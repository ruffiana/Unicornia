from enum import Enum
import json
import logging

import requests

from . import const


class Patterns(Enum):
    PULSE = "pulse"
    WAVE = "wave"
    FIREWORKS = "fireworks"
    EARTHQUAKE = "earthquake"


class Controller:
    API_URL_QR = "https://api.lovense.com/api/lan/getQrCode"
    BASE_REQ = {"token": const.LOVENSE_DEVELOPER_TOKEN, "apiVer": "1"}

    def __init__(self, parent=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.parent = parent
        self.guilds = self.parent.guilds

    def get_connection_qr(self, guild_id: str, uid: str):
        req = {
            **self.BASE_REQ,
            **{
                "uid": guild_id + ":" + uid,
            },
        }

        try:
            with requests.post(self.API_URL_QR, req) as response:
                return response.json().get("message", None)
        except (json.JSONDecodeError, AttributeError):
            return None

    def get_toys(self, guild_id: str):
        self.guilds._refresh()
        toys = []

        if guild_id not in self.guilds:
            return []

        for uid, user in self.guilds.get(guild_id).items():
            toys += [y.get("name") for x, y in user.get("toys").items()]

        return toys

    def stop(self, guild_id: str):
        return self._function(guild_id, "Stop", None, 0, 0)

    def pattern(self, guild_id: str, pattern, uid: str = None):
        self.guilds._refresh()

        if self.guilds.get(guild_id) is None:
            return False

        if uid is not None and uid not in self.guilds.get(guild_id):
            return False

        uids = [
            x.get("uid")
            for x in (
                self.guilds.get(guild_id).values()
                if uid is None
                else [self.guilds.get(guild_id).get(uid)]
            )
        ]
        req = {
            **self.BASE_REQ,
            **{
                "uid": ",".join(uids),
                "command": "Preset",
                "name": pattern,
                "timeSec": 0,
            },
        }
        with requests.post(self.API_URL_COMMAND, json=req, timeout=5) as response:
            return response.status_code == 200

    def vibrate(
        self, guild_id: str, uid: str = None, strength: int = 10, duration: int = 10
    ):
        return self._function(guild_id, "Vibrate", uid, strength, duration)

    def rotate(
        self, guild_id: str, uid: str = None, strength: int = 10, duration: int = 10
    ):
        return self._function(guild_id, "Rotate", uid, strength, duration)

    def pump(
        self, guild_id: str, uid: str = None, strength: int = 10, duration: int = 10
    ):
        return self._function(guild_id, "Pump", uid, strength, duration)

    # Send a command=Function request
    def _function(
        self,
        guild_id: str,
        action: str,
        uid: str = None,
        strength: int = 10,
        duration: int = 10,
    ):
        self.guilds._refresh()

        if guild_id not in self.guilds:
            return False

        if uid is not None and uid not in self.guilds.get(guild_id):
            return False

        if strength > 0:
            action += ":{}".format(strength)

        uids = [
            x.get("uid")
            for x in (
                self.guilds.get(guild_id).values()
                if uid is None
                else [self.guilds.get(guild_id).get(uid)]
            )
        ]
        req = {
            **self.BASE_REQ,
            **{
                "uid": ",".join(uids),
                "command": "Function",
                "action": action,
                "timeSec": duration,
            },
        }

        with requests.post(self.API_URL_COMMAND, json=req, timeout=5) as response:
            return response.status_code == 200
