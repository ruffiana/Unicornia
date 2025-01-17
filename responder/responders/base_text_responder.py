import asyncio
import re
from abc import ABC, abstractmethod

import discord

from .. import __version__
from .. import const


class BaseTextResponder(ABC):
    parent = None
    bot = None
    enabled: bool = False
    delete_after: int = None

    # The pattern to match in the message content -OR- a list of patterns to match.
    # If a list is provided, the first match will be used.
    pattern: str = ""
    patterns: list[str] = []

    # attributes used to generate regex flags
    ignore_case: bool = True
    multiline: bool = False
    dotall: bool = False
    verbose: bool = False

    @property
    def regex_flags(self):
        """Generate a combination of regex flags based on the object's attributes.

        This method checks the following attributes of the object:
        - `ignore_case`: If True, adds the `re.IGNORECASE` flag.
        - `multiline`: If True, adds the `re.MULTILINE` flag.
        - `dotall`: If True, adds the `re.DOTALL` flag.
        - `verbose`: If True, adds the `re.VERBOSE` flag.

        Returns:
            int: A bitwise OR combination of the selected regex flags.
        """
        flags = 0
        if self.ignore_case:
            flags |= re.IGNORECASE
        if self.multiline:
            flags |= re.MULTILINE
        if self.dotall:
            flags |= re.DOTALL
        if self.verbose:
            flags |= re.VERBOSE
        return flags

    @abstractmethod
    async def respond(
        self, message: discord.Message, matched_text: str, target: discord.Member = None
    ):
        """Define the response to the matched message

        Typically, you'll want to do something with the triggering message
        and then reply, send a message, or send an embed as the final result.
        """
        raise NotImplementedError("Subclasses must implement this method")

    async def delay_response(self, message: discord.Message, text: str):
        """Sends a delayed response to a Discord message.

        This function simulates typing by waiting for a calculated delay before sending a response.

        Args:
            message (discord.Message): The message object from the Discord API.
            text (str): The text content to be sent as a response.

        Returns:
            None
        """
        # Calculate the typing delay based on the length of the text with a max of 3 sec
        typing_delay = min(3, len(text) * 0.025)
        self.parent.logger.info(f"Typing delay: {typing_delay}")
        async with message.channel.typing():
            await asyncio.sleep(typing_delay)

    async def send_embed(
        self,
        message: discord.Message,
        title: str,
        description: str,
        thumbnail: str = None,
        fields: dict = None,
        footer: str = None,
        as_reply: bool = False,
        delay: bool = False,
        **kwargs,
    ):
        """Sends an embedded message to the specified Discord channel.

        Args:
            message (discord.Message): The original message that triggered the response.
            title (str): The title of the embed.
            description (str): The description of the embed.
            thumbnail (str, optional): URL of the thumbnail image to be displayed in the embed. Defaults to None.
            fields (dict, optional): A dictionary of fields to be added to the embed, where keys are field names and values are field values. Defaults to None.
            footer (bool, optional): Whether to include a footer in the embed. Defaults to False.
            as_reply (bool, optional): Whether to send the message as a reply. Defaults to False.
            delay (bool, optional): Whether to introduce a delay before sending the message. Defaults to False.

        Returns:
            None
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=const.UNICORNIA_BOT_COLOR,
        )
        if footer:
            embed.set_footer(
                text=footer,
                icon_url=self.bot.user.avatar.url,
            )

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if fields:
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=False)

        if delay:
            await self.delay_response(message, description)

        if as_reply:
            try:
                await message.channel.reply(embed=embed, **kwargs)
            except discord.HTTPException as e:
                self.parent.logger.error(f"Failed to send embed reply: {e}")
        else:
            try:
                await message.channel.send(embed=embed, **kwargs)
            except discord.HTTPException as e:
                self.parent.logger.error(f"Failed to send embed message: {e}")

    async def send_message(
        self,
        message: discord.Message,
        text: str,
        as_reply: bool = False,
        delay: bool = False,
        **kwargs,
    ):
        """Sends a message to the specified Discord channel.

        This function first calls `delay_response` to introduce a delay before sending the message.
        Then, it sends the provided text to the channel where the original message was received.

        Args:
            message (discord.Message): The original message object from the Discord channel.
            text (str): The text content to be sent as a message.
            as_reply (bool, optional): Whether to send the message as a reply. Defaults to False.
            delay (bool, optional): Whether to introduce a delay before sending the message. Defaults to False.

        Returns:
            None
        """
        if delay:
            await self.delay_response(message, text)

        if as_reply:
            try:
                await message.reply(text, **kwargs)
            except discord.HTTPException as e:
                self.parent.logger.error(f"Failed to send message reply: {e}")
        else:
            try:
                await message.channel.send(content=text, **kwargs)
            except discord.HTTPException as e:
                self.parent.logger.error(f"Failed to send message: {e}")

    def __str__(self):
        return f"{self.__class__.__name__}(pattern={self.pattern})"
