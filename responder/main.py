import logging
import re

import discord

from redbot.core import commands
from redbot.core.bot import Red

from . import __version__
import importlib
import glob
from pathlib import Path
from .text_responders import TextResponder
from . import const


class ResponderCog(commands.Cog):
    RESPONDERS_PATH = Path(__file__).parent / "responders"
    RESPONDER_FILE_PATHS = [Path(p) for p in glob.glob(str(RESPONDERS_PATH / "*.py"))]

    def __init__(self, bot: Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOG_LEVEL)

        self.responders = self.collect_responders()

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    def collect_responders(self):
        responders = []

        for filepath in self.RESPONDER_FILE_PATHS:
            module_name = filepath.stem

            if module_name == "__init__":
                continue

            module = importlib.import_module(
                f".responders.{module_name}", package=__package__
            )
            self.logger.debug(f"Loaded module: {module}")

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and attr is not TextResponder
                    and issubclass(attr, TextResponder)
                    and getattr(attr, "enabled", False)
                ):
                    self.logger.debug(f'Adding "{attr_name}" to responders')
                    class_obj = attr(parent=self, bot=self.bot)
                    responders.append(class_obj)

        return responders

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from all bots
        if message.author.bot:
            return

        for responder in self.responders:
            self.logger.debug(f"Checking responder: {responder}")
            flags = re.IGNORECASE if responder.ignore_case else 0
            self.logger.debug(f"Checking pattern: {responder.pattern}")
            match = re.search(responder.pattern, message.content, flags)
            if match:
                self.logger.debug(f"Match: {match}")
                return await responder.response(message)
