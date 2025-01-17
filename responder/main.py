import glob
import importlib
import logging
from pathlib import Path
import re

import discord
from redbot.core import commands
from redbot.core.bot import Red

from . import __version__
from . import const
from .responders.base_text_responder import BaseTextResponder
from .responders.base_rate_responder import BaseRateResponder


class ResponderCog(commands.Cog):
    RESPONDERS_PATH = Path(__file__).parent / "responders"
    RESPONDER_FILE_PATHS = [Path(p) for p in glob.glob(str(RESPONDERS_PATH / "*.py"))]

    # Pattern used to separate potential commands from target members
    # ^(.*?): Captures any characters (non-greedy) at the beginning of the string as trigger.
    # \s+: Matches one or more whitespace characters.
    # (<@!?\d+>|\d+|@\w+|@\w+\s\w+): Matches and captures the member part, which can be a user mention, user ID, or username.
    COMMAND_USER_PATTERN = re.compile(r"\A^(.*?)\s+(<@!?\d+>|\d+|@\w+|@\w+\s\w+)$")

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
                    and attr is not any([BaseTextResponder, BaseRateResponder])
                    and issubclass(attr, BaseTextResponder)
                    and getattr(attr, "enabled", False)
                ):
                    self.logger.debug(f'Adding "{attr_name}" to responders')
                    class_obj = attr(parent=self, bot=self.bot)
                    responders.append(class_obj)

        return responders

    async def get_target_member(self, message, arg):
        member = None

        # Try to get member by mention
        if re.match(r"<@!?\d+>", arg):
            member_id = int(re.findall(r"\d+", arg)[0])
            member = message.guild.get_member(member_id)

        # Try to get member by user ID
        if not member and arg.isdigit():
            member = message.guild.get_member(int(arg))
            if not member:
                try:
                    member = await message.guild.fetch_member(int(arg))
                except discord.NotFound:
                    member = None

        # Try to get member by username
        if not member:
            for m in message.guild.members:
                if str(m) == arg or f"{m.name}#{m.discriminator}" == arg:
                    member = m
                    break

        return member

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from all bots
        if message.author.bot:
            return

        match = self.COMMAND_USER_PATTERN.match(message.content.strip())
        if match:
            trigger = match.group(1).strip()
            target = match.group(2).strip()
        else:
            trigger = message.content
            target = None

        if target:
            target_member = await self.get_target_member(message, target)
            if target_member is None:
                return await message.reply(f'Unable to find a member using "{target}".')
        else:
            target_member = message.author

        for responder in self.responders:
            self.logger.debug(
                f"Checking responder: {responder} using pattern: {responder.pattern}"
            )

            # Check if the responder has a list of patterns
            if hasattr(responder, "patterns") and responder.patterns:
                for pattern in responder.patterns:
                    match = re.search(pattern, trigger, responder.regex_flags)
                    if match:
                        self.logger.debug(f"Match: {match}")
                        return await responder.respond(message, target=target_member)
            else:
                match = re.search(responder.pattern, trigger, responder.regex_flags)
                if match:
                    self.logger.debug(f"Match: {match}")
                    return await responder.respond(message, target=target_member)
