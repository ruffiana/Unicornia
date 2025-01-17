import discord
from redbot.core.bot import Red

from .text_responder_base import TextResponderBase


class TableUnflipResponder(TextResponderBase):
    enabled = True
    pattern = r"\(╯°□°\)╯︵ ┻━┻"
    ignore_case = True

    # List of user IDs that will never get a response
    never_respond = []

    def __init__(self, parent, bot: Red):
        super().__init__()
        self.parent = parent
        self.bot = bot

    async def respond(self, message: discord.Message, target: discord.Member = None):
        if message.author.id in self.never_respond:
            return

        await self.send_message(message, f"┬─┬ノ( º _ ºノ)", as_reply=True, delay=True)
