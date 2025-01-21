import glob
import importlib
import logging
import re
from pathlib import Path
from typing import Union

import discord
from redbot.core import commands
from redbot.core.bot import Red

from . import __version__, const
from .responders.base_rate_responder import BaseRateResponder
from .responders.base_text_responder import BaseTextResponder
from .unicornia import discord as unicornia_discord


class ResponderCog(commands.Cog):
    RESPONDERS_PATH = Path(__file__).parent / "responders"
    RESPONDER_FILE_PATHS = [Path(p) for p in glob.glob(str(RESPONDERS_PATH / "*.py"))]
    ALLOWED_CHANNEL_IDS = {
        # Ruffiana's Playground - redbot
        1318299981668552735,
        # bot commands
        686096388018405408,
        # bot dungeon
        1081656723904921651,
        # comfy chat
        778700678851723295,
        # horny jail
        686091486327996459,
        # bot spam
        686092688059400454,
    }

    # Pattern used to separate potential commands from target members
    # ^(.*?): Captures any characters (non-greedy) at the beginning of the string as trigger.
    # \s+: Matches one or more whitespace characters.
    # (<@!?\d{17,19}>|\d{17,19}|@\w+|@\w+\s\w+): Matches and captures the member part,
    # which can be a user mention, user ID, or username.
    # COMMAND_USER_PATTERN = re.compile(
    #     r"^(.*?)\s+(<@!?\d{17,19}>|\d{17,19}|@\w+|@\w+\s\w+)$"
    # )
    # using just the user mention/ user ID pattern for now
    COMMAND_USER_PATTERN = re.compile(r"^(.*?)\s+(<@!?\d{17,19}>|\d{17,19})$")

    def __init__(self, bot: Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOG_LEVEL)

        self.responders = self._init_responders()

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    def _init_responders(self):
        """Collect all responder classes from the responders directory and instantiates them."""
        ignore_classes = [BaseTextResponder, BaseRateResponder]
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
                    and attr is not any(ignore_classes)
                    and issubclass(attr, BaseTextResponder)
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

        # Check if the message is in an allowed channel
        if message.channel.id not in self.ALLOWED_CHANNEL_IDS:
            return

        match = self.COMMAND_USER_PATTERN.match(message.content.strip())
        if match:
            trigger = match.group(1).strip()
            target_key = match.group(2).strip()
        else:
            trigger = message.content
            target_key = None

        for responder in self.responders:
            self.logger.debug(
                f"Checking responder: {responder} using patterns: {responder.patterns}"
            )

            # Make sure the responder has a valid list patterns to match against
            if not hasattr(responder, "patterns") or not responder.patterns:
                self.logger.error(f"Responder {responder} has no patterns!")
                continue

            for pattern in responder.patterns:
                match = re.search(pattern, trigger, responder.regex_flags)
                if not match:
                    self.logger.debug(f"No match for {trigger} in pattern: {pattern}")
                    continue

                # Check if the responder is on cooldown
                if responder.is_on_cooldown():
                    if responder.silent_cooldown:
                        return
                    return await message.reply(
                        f"Please wait {responder.get_cooldown_remaining()}s before using this command again."
                    )

                # We have a valid responder pattern and a target key
                if target_key:
                    context = await self.bot.get_context(message)
                    target_member = await unicornia_discord.get_member(
                        context, target_key
                    )
                    if target_member is None:
                        return await message.reply(
                            f'Unable to find a member using "{target_key}".'
                        )
                # No target key, use the message author
                else:
                    target_member = message.author

                self.logger.debug(
                    f"message: {message}, target_member: {target_member}, match: {match}"
                )

                # Update the last called time for the responder and call the respond method
                responder.update_last_called()
                return await responder.respond(message, target_member, match)
