"""Base test responder class
This module defines the `BaseTextResponder` class, an abstract base class
for creating text responders in a Discord bot.

The `BaseTextResponder` class provides the following functionalities:
- Define patterns to match in message content.
- Generate regex flags based on object attributes.
- Abstract method `respond` to be implemented by subclasses for defining responses to matched messages.
- Methods for sending delayed responses, embedded messages, and plain text messages to Discord channels.

Attributes:
    parent: The parent object/main cog that instantiates the responder.
    bot: The Discord/Redbot bot instance. Passed in from main cog function.

    enabled: Flag that indicates whether the responder is enabled.

    patterns The patterns to match in the message content.
    For simplicity, this is always defined as a list of strings.

    Attributes used to generate regex flags:
    ignore_case (bool): If True, adds the `re.IGNORECASE` flag to regex.
    multiline (bool): If True, adds the `re.MULTILINE` flag to regex.
    dotall (bool): If True, adds the `re.DOTALL` flag to regex.
    verbose (bool): If True, adds the `re.VERBOSE` flag to regex.

    delete_after (int): The time in seconds after which the response
    message should be deleted. You generally never want to delete the
    message, but it's here if you need it.
    
    always_respond (list[int]): List of user IDs to always respond to.
    These can be extended in the subclass to include more users.

    never_respond (list[int]): List of user IDs to never respond to.
    These can be extended in the subclass to include more users.
"""

import asyncio
import re
from abc import ABC, abstractmethod
from typing import Union

import discord

from .. import __version__, const
from .. import const


class BaseTextResponder(ABC):
    parent = None
    bot = None
    enabled: bool = False
    delete_after: int = None

    # The pattern(s) to match in the message content. This is defined as a list so that
    # we can treat them the sa
    patterns: Union[str, list[str]] = []
    target_member: discord.Member = None

    # attributes used to generate regex flags
    ignore_case: bool = True
    multiline: bool = False
    dotall: bool = False
    verbose: bool = False

    always_respond: list[int] = const.ALWAYS_RESPOND
    never_respond: list[int] = const.NEVER_RESPOND

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
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
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
        return f"{self.__class__.__name__}(patterns={self.patterns})"
