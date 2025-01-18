"""Table Unflip Responder

Simple call/response responder that unflips tables.
"""

import re

import discord
from redbot.core.bot import Red

from .base_text_responder import BaseTextResponder
from .. import const


class TableUnflipResponder(BaseTextResponder):
    enabled = True
    patterns = [r"\(╯°□°\)╯︵ ┻━┻"]
    ignore_case = True

    def __init__(self, parent, bot: Red):
        super().__init__()
        self.parent = parent
        self.bot = bot

        self.never_respond.extend([const.KIRIN_ID])

    async def respond(
        self,
        message: discord.Message,
        target: discord.Member,
        match: re.Match,
    ):
        if message.author.id in self.never_respond:
            return

        await self.send_message(message, f"┬─┬ノ( º _ ºノ)", as_reply=True, delay=True)
