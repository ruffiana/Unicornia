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
    ALLOWED_ROLE_IDS = [
        700121551483437128,  # supporter role
        696020813299580940,  # staff role
        707303996389589045,  # cutie of the month
    ]

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
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def judge(self, ctx, *, text: str = None):
        if not ctx.author.guild_permissions.administrator and not any(
            role.id in self.ALLOWED_ROLE_IDS for role in ctx.author.roles
        ):
            return await ctx.send(
                "This command can only be used by supporters, staff, and Cutie of the Month."
            )

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

            return await ctx.send(embed=embed, file=file)

        # if the command wasn't successful, reset the cooldown for this command
        self.reset_cooldown(ctx, "judge")

    def reset_cooldown(self, ctx: commands.Context, command_name: str):
        """Reset the cooldown for the invoking user."""
        command = self.bot.get_command(command_name)
        if command is not None:
            bucket = command._buckets.get_bucket(ctx)
            bucket.reset()
            self.logger.debug(f'Reset cooldown on"{command_name}" command.')
        else:
            self.logger.error(f'Invalid command name: "{command_name}".')
