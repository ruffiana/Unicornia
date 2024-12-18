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
    API_URL_COMMAND = "https://api.lovense.com/api/lan/v2/command"
    API_URL_QR = "https://api.lovense.com/api/lan/getQrCode"
    BASE_REQ = {"token": const.LOVENSE_DEVELOPER_TOKEN, "apiVer": "1"}

    def __init__(self, parent=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.parent = parent
        self.guilds = self.parent.guilds

    def get_connection_qr(self, guild_id: str, user_id: str):
        """Get a QR code from Lovense to connect the user

        Args:
            guild_id (str): _description_
            user_id (str): _description_

        Returns:
            _type_: _description_
        """
        req = {
            **self.BASE_REQ,
            **{
                "uid": f"{guild_id}:{user_id}",
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

        if guild_id not in self.guilds.ids:
            return []

        for _, user in self.guilds.get(guild_id).items():
            toys += [y.get("name") for x, y in user.get("toys").items()]

        return toys

    def stop(self, guild_id: str):
        return self._function(guild_id, "Stop", None, 0, 0)

    def pattern(self, guild_id: str, pattern, user_id: str = None):
        self.guilds._refresh()

        if self.guilds.get(guild_id) is None:
            return False

        if user_id is not None and user_id not in self.guilds.get(guild_id):
            return False

        user_ids = [
            x.get("uid")
            for x in (
                self.guilds.get(guild_id).values()
                if user_id is None
                else [self.guilds.get(guild_id).get(user_id)]
            )
        ]
        req = {
            **self.BASE_REQ,
            **{
                "uid": ",".join(user_ids),
                "command": "Preset",
                "name": pattern,
                "timeSec": 0,
            },
        }
        with requests.post(self.API_URL_COMMAND, json=req, timeout=5) as response:
            return response.status_code == 200

    def vibrate(
        self, guild_id: str, user_id: str = None, strength: int = 10, duration: int = 10
    ):
        return self._function(guild_id, "Vibrate", user_id, strength, duration)

    def rotate(
        self, guild_id: str, user_id: str = None, strength: int = 10, duration: int = 10
    ):
        return self._function(guild_id, "Rotate", user_id, strength, duration)

    def pump(
        self, guild_id: str, user_id: str = None, strength: int = 10, duration: int = 10
    ):
        return self._function(guild_id, "Pump", user_id, strength, duration)

    # Send a command=Function request
    def _function(
        self,
        guild_id: str,
        action: str,
        user_id: str = None,
        strength: int = 10,
        duration: int = 10,
    ):
        self.guilds._refresh()

        if guild_id not in self.guilds.ids:
            return False

        if not user_id or user_id not in self.guilds.get(guild_id):
            return False

        if strength > 0:
            action += ":{}".format(strength)

        user_ids = [
            x.get("uid")
            for x in (
                self.guilds.get(guild_id).values()
                if user_id is None
                else [self.guilds.get(guild_id).get(user_id)]
            )
        ]
        req = {
            **self.BASE_REQ,
            **{
                "uid": ",".join(user_ids),
                "command": "Function",
                "action": action,
                "timeSec": duration,
            },
        }

        with requests.post(self.API_URL_COMMAND, json=req, timeout=5) as response:
            return response.status_code == 200
