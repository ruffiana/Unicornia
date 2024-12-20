import logging
import discord
from redbot.core import commands
from redbot.core.bot import Red
import re

from .scoreboards import Generator
from . import __version__, __author__
from . import strings


class JudgeCog(commands.Cog):
    EMBED_COLOR = discord.Color.from_str("#9401fe")
    EMBED_FOOTER = f"Judge Cog ({__version__}) - by: {__author__}"
    TEMP_FILENAME = "judges_score.jpg"

    def __init__(self, bot: Red):
        self.bot = bot

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

        self.image_maker = Generator()

    @staticmethod
    def convert_mentions(text: str, member: discord.User):
        # matches @<[userID]>
        mention_regex = re.compile(r"<@!?(\d+)>")
        text = mention_regex.sub(member.display_name, text)
        return text

    @commands.command(name="judge", aliases=["score"])
    @commands.has_permissions(administrator=True)
    async def judge(self, ctx, *, text: str = None):

        if ctx.message.mentions:
            member = ctx.message.mentions[0]
            text = self.convert_mentions(text, member)
            # get color of member's top role as RGB
            color = member.color.to_rgb()
        else:
            color = None

        if text:
            text = strings.replace_pronouns(text)
            text = strings.remove_emojis(text)

        self.logger.debug(f"color: {color}")

        # Indicate that the bot is typing
        async with ctx.typing():
            output_image_path = self.image_maker.create(text=text, text_color=color)

            file = discord.File(fp=output_image_path, filename=self.TEMP_FILENAME)

            # Create the embed object
            embed = discord.Embed(color=self.EMBED_COLOR)

            footer = self.EMBED_FOOTER
            embed.set_footer(text=footer, icon_url=self.bot.user.avatar.url)
            embed.set_image(url=f"attachment://{self.TEMP_FILENAME}")

            await ctx.send(embed=embed, file=file)
