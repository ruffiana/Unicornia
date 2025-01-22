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

    # Pattern used to separate potential trigger from the target member
    # ^(.*?): Captures any characters (non-greedy) at the beginning of the string as trigger.
    # \s+: Matches one or more whitespace characters.
    # (<@!?\d{17,19}>|\d{17,19}): Matches and captures a mention or user ID.
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

    def _get_responder(
        self, trigger: str
    ) -> Union[tuple[BaseTextResponder, re.Match], tuple[None, None]]:
        """Retrieve the appropriate responder based on the given trigger.

        This method iterates through the list of responders and checks if any of them
        have patterns that match the provided trigger string. If a match is found, the
        corresponding responder is returned. If no match is found, None is returned.

        Args:
            trigger (str): The trigger string to match against the responder patterns.

        Returns:
            Union[BaseTextResponder, None]: The responder that matches the trigger, or None if no match is found.
        """
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
                if match:
                    return responder, match
                else:
                    self.logger.debug(f"No match for {trigger} in pattern: {pattern}")

        return None, None

    async def _get_target_member(
        self, message: discord.Message, target_key: Union[str, None]
    ) -> discord.Member:
        """Retrieves the target member from a message.

        If the target_key is None, the author of the message is returned.
        Otherwise, it attempts to find and return the member specified by the target_key.

        Args:
            message (discord.Message): The message object containing the author and context.
            target_key (Union[str, None]): The key used to identify the target member. If None, the message author is returned.

        Returns:
            discord.Member: The member object corresponding to the target_key or the message author if target_key is None.
        """
        if target_key is None:
            return message.author

        context = await self.bot.get_context(message)
        return await unicornia_discord.get_member(context, target_key)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Event listener that is called when a message is created and sent to a channel.

        Args:
            message (discord.Message): The message that was sent.

        Returns:
            None

        Behavior:
            - Ignores messages sent by bots.
            - Ignores messages sent in channels not listed in ALLOWED_CHANNEL_IDS.
            - Extracts the trigger and target key from the message content using COMMAND_USER_PATTERN.
            - Finds a responder for the trigger.
            - Checks if the responder is on cooldown and replies with a cooldown message if necessary.
            - Attempts to find the target member using the target key.
            - Updates the responder's last called time and calls the responder's respond method.
        """

        # Ignore messages from all bots
        if message.author.bot:
            return

        # Check if the message is in an allowed channel
        if message.channel.id not in self.ALLOWED_CHANNEL_IDS:
            return

        # Separate trigger from potential target member
        match = self.COMMAND_USER_PATTERN.match(message.content.strip())
        if match:
            trigger = match.group(1).strip()
            target_key = match.group(2).strip()
        else:
            trigger = message.content
            target_key = None

        # Try and find a responder for any triggers in the message
        responder, responder_match = self._get_responder(trigger)
        if responder is None:
            return

        # Check if the responder is on cooldown
        if (
            responder.is_on_cooldown()
            and not message.author.guild_permissions.administrator
        ):
            if responder.silent_cooldown:
                return
            return await message.reply(
                f"Please wait {responder.get_cooldown_remaining()}s before using this command again."
            )

        # Get the target discord.Member object
        target_member = await self._get_target_member(message, target_key)
        if target_member is None:
            await message.reply(f'Unable to find a member using "{target_key}".')
            return None

        # Update the last called time for the responder and call the respond method
        responder.update_last_called()

        self.logger.debug(
            f"Calling responder: {responder}\nmessage: {message.content}\ntarget_member: {target_member}\nmatch: {responder_match}"
        )
        return await responder.respond(message, target_member, responder_match)
