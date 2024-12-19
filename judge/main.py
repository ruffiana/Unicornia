import logging
from discord import File
from redbot.core import commands
from redbot.core.bot import Red

from .image_generator import JudgesScoreboardGenerator
from . import __version__


class JudgesCog(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

        self.generator = JudgesScoreboardGenerator()

    @commands.command(aliases=["score"])
    async def judge(self, ctx, *, text: str = None):
        output_image_path = self.generator.create(text=text)
        file = File(fp=output_image_path, filename=f"judges_score.jpg")
        await ctx.send(f"The judges scores...", file=file)
