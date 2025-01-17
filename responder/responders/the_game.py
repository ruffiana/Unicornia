import discord
from redbot.core.bot import Red

from .text_responder_base import TextResponderBase


class TheGameResponder(TextResponderBase):
    enabled = True
    pattern = r"\bthe game\b"
    ignore_case = True

    # List of user IDs that will always get a response
    always_respond = []
    # List of user IDs that will never get a response
    never_respond = []

    def __init__(self, parent, bot: Red):
        super().__init__()
        self.parent = parent
        self.bot = bot

    async def respond(self, message: discord.Message, target: discord.Member = None):
        if message.author.id in self.never_respond:
            return

        await self.send_message(
            message, f"You just lost the game.", as_reply=True, delay=True
        )
