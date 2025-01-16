import random
import re

import discord
from redbot.core.bot import Red
import asyncio

from .. import const
from ..text_responders import TextResponder


class Daddy(TextResponder):
    enabled = True
    ignore_case = True
    # Match "i'm | i am" at the beginning of the message
    pattern = r"\A(?:i'?\s?a?m\s+)"

    # List of user IDs that will always get a response
    always_respond = [474075064069783552]
    # List of user IDs that will never get a response
    never_respond = []

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot

    async def response(self, message: discord.Message):
        if message.author.id in self.never_respond:
            return

        flags = re.IGNORECASE if self.ignore_case else 0
        match = re.match(self.pattern, message.content, flags)
        name = message.content[match.end() :].strip()

        chance = 50 / max(1, len(name))
        self.parent.logger.debug(f"{name} = {chance}% chance to respond")

        if message.author.id in self.always_respond or random.randint(0, 99) < chance:
            await self.reply(message, f"Hi, {name}! I'm your daddy...")
