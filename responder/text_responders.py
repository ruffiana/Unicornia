from abc import ABC, abstractmethod

import discord
import asyncio

from . import const
from . import __version__


class TextResponder(ABC):
    parent = None
    bot = None
    enabled = False
    ignore_case = True
    delete_after = None
    pattern = ""

    @abstractmethod
    async def response(self, message: discord.Message, matched_text: str):
        """Define the response to the matched message

        Typically, you'll want to do something with the triggering message
        and then reply, send a message, or send an embed as the final result.
        """
        pass

    async def delay(self, message: discord.Message, text: str):
        typing_delay = min(3, len(text) * 0.05)
        self.parent.logger.info(f"Typing delay: {typing_delay}")
        async with message.channel.typing():
            await asyncio.sleep(typing_delay)

    async def embed(
        self,
        message: discord.Message,
        title: str,
        description: str,
        thumbnail: str = None,
        fields: dict = None,
    ):

        await self.delay(message, description)
        embed = discord.Embed(
            title=title,
            description=description,
            color=const.UNICORNIA_BOT_COLOR,
        )
        embed.set_footer(
            text=f"Responder Cog - v{__version__}", icon_url=self.bot.user.avatar.url
        )
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if fields:
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=False)

        await message.channel.send(embed=embed)

    async def message(self, message: discord.Message, text: str):
        await self.delay(message, text)
        return await message.channel.send(text)

    async def reply(self, message: discord.Message, text: str):
        await self.delay(message, text)
        return await message.reply(text)

    def __str__(self):
        return f"{self.__class__.__name__}(pattern={self.pattern})"

    def __repr__(self):
        return f"<{self.__class__.__name__} pattern={self.pattern}>"
