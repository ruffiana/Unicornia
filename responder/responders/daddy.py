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

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot

    async def response(self, message: discord.Message):
        flags = re.IGNORECASE if self.ignore_case else 0
        match = re.match(self.pattern, message.content, flags)
        name = message.content[match.end() :].strip()

        chance = 50 / max(1, len(name))
        self.parent.logger.debug(f"{name} = {chance}% chance to respond")

        if random.randint(0, 99) < chance:
            typing_delay = min(len(name) * 0.1, 5)
            async with message.channel.typing():
                await asyncio.sleep(typing_delay)
            return await message.reply(f"Hi, {name}! I'm your daddy...")
            # title = f"Hi {name}!"
            # description = "I'm your daddy..."
            # return await self.send_embed(message, title, description)

    # async def send_embed(self, message: discord.Message, title: str, description: str):
    #     embed = discord.Embed(
    #         title=title,
    #         description=description,
    #         color=const.UNICORNIA_BOT_COLOR,
    #     )
    #     embed.set_thumbnail(url=self.bot.user.avatar.url)
    #     await message.channel.send(embed=embed)
