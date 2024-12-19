import logging
import discord
from redbot.core import commands
from redbot.core.bot import Red

from .image_generator import JudgesScoreboardGenerator
from . import __version__, __author__


class JudgesCog(commands.Cog):
    EMBED_COLOR = discord.Color.from_str("#9401fe")
    EMBED_FOOTER = f"Judge Cog ({__version__}) - by: {__author__}"

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
        temp_filename = "judges_score.jpg"
        output_image_path = self.generator.create(text=text)
        file = discord.File(fp=output_image_path, filename=temp_filename)

        # create the embed object
        embed = discord.Embed(
            description="The judges scores...", color=self.EMBED_COLOR
        )

        footer = self.EMBED_FOOTER
        embed.set_footer(text=footer, icon_url=self.bot.user.avatar.url)
        embed.set_image(url=f"attachment://{temp_filename}")

        await ctx.send(embed=embed, file=file)
