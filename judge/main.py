import logging
import discord
from redbot.core import commands
from redbot.core.bot import Red

from .image_generator import JudgesScoreboardGenerator
from . import __version__, __author__


class JudgesCog(commands.Cog):
    EMBED_COLOR = discord.Color.from_str("#9401fe")
    EMBED_FOOTER = f"Judge Cog ({__version__}) - by: {__author__}"
    TEMP_FILENAME = "judges_score.jpg"

    def __init__(self, bot: Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

        self.generator = JudgesScoreboardGenerator()

    @commands.command(name="judge", aliases=["score"])
    @commands.has_permissions(administrator=True)
    async def judge(self, ctx, *, text: str = None):
        if ctx.message.mentions:
            mentioned_user = ctx.message.mentions[0]
            user_name = mentioned_user.display_name
            text = text.replace(f"<@{mentioned_user.id}>", user_name)
            color = mentioned_user.color.to_rgb()
        else:
            color = None
        self.logger.debug(f"color: {color}")

        output_image_path = self.generator.create(text=text, text_color=color)

        file = discord.File(fp=output_image_path, filename=self.TEMP_FILENAME)

        # Create the embed object
        embed = discord.Embed(
            description="The judges scores...", color=self.EMBED_COLOR
        )

        footer = self.EMBED_FOOTER
        embed.set_footer(text=footer, icon_url=self.bot.user.avatar.url)
        embed.set_image(url=f"attachment://{self.TEMP_FILENAME}")

        await ctx.send(embed=embed, file=file)
