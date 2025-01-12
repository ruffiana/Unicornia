import asyncio
import datetime
import logging
import typing

import discord
from redbot.core import checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list

from . import __version__
from .actions import Actions
from .config import ConfigManager
from .gifts import Gifts
from .predicates import CustomMessagePredicate
from .user import MarriageUser


class Marriage(commands.Cog):
    """Marry, divorce, perform actions, and give gifts to other members."""

    COG_IDENTIFIER = 5465461324979524
    CONSENT_TIMEOUT = 2  # 120  # seconds
    NONE_USER_MESSAGE = (
        'I couldn\'t find anyone using "{key}". Try using their ID or mention.'
    )

    def __init__(self, bot: Red):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        self.bot = bot
        self.config_manager = ConfigManager(bot=self.bot, parent=self)
        self.actions = Actions(bot=self.bot, parent=self)
        self.gifts = Gifts(bot=self.bot, parent=self)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    @staticmethod
    def format_help_for_context(ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f"{context}\n\nVersion: {__version__}"

    @commands.group(autohelp=True, aliases=["marriage"])
    @commands.guild_only()
    @checks.admin()
    async def marryset(self, ctx: commands.Context):
        """Various Marriage settings."""
        # if ctx.invoked_subcommand is None:
        #     await self.marryset_settings(ctx)

    @marryset.command(name="multiple")
    @commands.is_owner()
    async def marryset_multiple(self, ctx: commands.Context, state: bool):
        """Enable/disable whether members can be married to multiple people at once."""
        await self.config_manager.set_multiple_spouses(state)
        await ctx.send(f"Members {'can' if state else 'cannot'} marry multiple people.")

    @marryset.command(name="settings")
    @commands.is_owner()
    async def marryset_settings(self, ctx: commands.Context):
        """See current settings."""
        multiple_spouses = await self.config_manager.multiple_spouses
        self.logger.debug(f"Multiple spouses: {multiple_spouses}")
        actions = self.actions.as_list()
        gifts = self.gifts.as_list()
        self.logger.debug(f"Actions: {actions}")
        self.logger.debug(f"Gifts: {gifts}")

        embed = discord.Embed(
            colour=await ctx.embed_colour(), timestamp=datetime.datetime.now()
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.title = "**__Marriage settings:__**"
        embed.add_field(name="Multiple spouses:", value=multiple_spouses)
        embed.add_field(name="Actions:", value=humanize_list(actions))
        embed.add_field(name="Gifts:", value=humanize_list(gifts))

        await ctx.send(embed=embed)

    @marryset.group(autohelp=True, name="actions", aliases=["action", "perform"])
    async def marryset_actions(self, ctx: commands.Context):
        """Custom actions"""
        # if ctx.invoked_subcommand is None:
        #     await self.marryset_actions_list(ctx)

    @marryset_actions.command(name="show")
    @commands.is_owner()
    async def marryset_actions_show(self, ctx: commands.Context, action_name: str):
        """Show a custom action."""
        display = self.actions.show(action_name)
        await ctx.send(box(display, lang="asciidoc"))

    @marryset_actions.command(name="list")
    @commands.is_owner()
    async def marryset_actions_list(self, ctx: commands.Context):
        """Show custom action."""
        actions = self.actions.as_list()
        await ctx.send(f"Available actions:")
        actions_list = "\n".join(actions)
        await ctx.send(box(actions_list, lang="asciidoc"))

    @marryset.group(autohelp=True, name="gifts", aliases=["gift", "give"])
    async def marryset_gifts(self, ctx: commands.Context):
        """Custom gifts"""
        # if ctx.invoked_subcommand is None:
        #     await self.marryset_gifts_list(ctx)

    @marryset_gifts.command(name="show")
    @commands.is_owner()
    async def marryset_gifts_show(self, ctx: commands.Context, gift_name: str):
        """Show properties of a gift."""
        display = self.gifts.show(gift_name)
        await ctx.send(box(display, lang="asciidoc"))

    @marryset_gifts.command(name="list")
    @commands.is_owner()
    async def marryset_gifts_list(self, ctx: commands.Context):
        """Show custom gift."""
        gifts = self.gifts.as_list()
        gifts_list = "\n".join(gifts)
        await ctx.send(f"Available gifts:")
        await ctx.send(box(gifts_list, lang="asciidoc"))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def about(
        self,
        ctx: commands.Context,
        target: typing.Optional[typing.Union[int, str]] = None,
    ):
        """Display your or someone else's about"""
        if not target:
            target_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            target_user = MarriageUser.get_user(ctx, target, cog=self)

        if not target_user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        embed = discord.Embed(colour=target_user.color)
        embed.set_author(
            name=f"{target_user.display_name}'s Profile",
            icon_url=target_user.avatar.url,
        )
        embed.set_footer(
            text=f"{target_user.display_name}#{target_user.discriminator} ({target_user.id}) - Marriage v{__version__}"
        )
        embed.set_thumbnail(url=target_user.avatar.url)

        about = await target_user.about
        embed.add_field(name="About:", value=about, inline=False)

        status = await target_user.relationship_status
        self.logger.debug(f"Status: {status}")
        embed.add_field(name="Status:", value=status)

        spouses = await target_user.spouses_as_list()
        if spouses:
            name = "Spouses:" if spouses and len(spouses) > 1 else "Spouse:"
            value = humanize_list(spouses) if spouses else "None"
            embed.add_field(name=name, value=value)

        embed.add_field(name="Crush:", value=await target_user.crush)

        embed.add_field(name="Contentment:", value=await target_user.contentment)

        marriage_count = await target_user.marriage_count
        embed.add_field(
            name="Been married:",
            value=(f'{marriage_count} {"time" if marriage_count == 1 else "times"}'),
        )

        exes = await target_user.exes_as_list()
        if exes:
            name = "Ex spouses:" if len(exes) > 1 else "Ex spouse:"
            value = "None" if not exes else humanize_list(exes)
            embed.add_field(name=name, value=value)

        value = await target_user.gifts_as_text()
        self.logger.debug(f"Gifts: {value}")
        embed.add_field(name="Available gifts:", value=value)

        await ctx.send(embed=embed)

    @about.command(name="add", aliases=["set"])
    async def about_add(self, ctx: commands.Context, *, about: str):
        """Add your about text

        Maximum is 1000 characters."""
        if len(about) > 1000:
            return await ctx.send(
                f"Uh oh, this is not an essay. {len(about)}/1000 characters."
            )

        user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        await user.set_about(about)
        await ctx.tick()

    @commands.guild_only()
    @commands.command()
    async def exes(
        self,
        ctx: commands.Context,
        target: typing.Optional[typing.Union[int, str]] = None,
    ):
        """Display your or someone else's exes."""
        if not target:
            user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            user = MarriageUser.get_user(ctx, target, cog=self)

        if not user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        exes = await user.exes_as_list()
        if not exes:
            return await ctx.send(f"{user.display_name} has no exes.")
        else:
            await ctx.send(
                f"{user.display_name}'s {'exes are' if len(exes) > 1 else 'ex is'}: {humanize_list(exes)}"
            )

    @commands.guild_only()
    @commands.command()
    async def spouses(
        self,
        ctx: commands.Context,
        target: typing.Optional[typing.Union[int, str]] = None,
    ):
        """Display your or someone else's spouses."""
        if not target:
            user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            user = MarriageUser.get_user(ctx, target, cog=self)

        if not user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        user = MarriageUser(bot=self.bot, parent=self, user=user)
        spouses = await user.spouses_as_list()
        if not spouses:
            return await ctx.send(f"{user.display_name} has no spouses.")
        else:
            await ctx.send(
                f"{user.display_name}'s {'spouses are' if len(spouses) > 1 else 'spouse is'}: {humanize_list(spouses)}"
            )

    @commands.guild_only()
    @commands.command()
    async def crush(
        self,
        ctx: commands.Context,
        target: typing.Optional[typing.Union[int, str]] = None,
    ):
        """Tell us who you have a crush on."""
        if not target:
            crush = await author_user.crush
            if crush != "None":
                return await ctx.send(f"Your current crush is: {crush}")
            else:
                return await ctx.send("You don't have a crush.")

        if target.lower() in ["none", "nobody", "remove", "clear"]:
            target_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
            await target_user.remove_crush()
            return await ctx.send("You no longer have a crush.")
        else:
            target_user = MarriageUser.get_user(ctx, target, cog=self)

        if not target_user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        if target_user.id == ctx.author.id:
            return await ctx.send("You cannot have a crush on yourself!")

        author_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        await author_user.set_crush(target_user)
        await ctx.tick()

    @commands.max_concurrency(1, commands.BucketType.channel, wait=True)
    @commands.guild_only()
    @commands.command()
    async def marry(self, ctx: commands.Context, target: typing.Union[int, str]):
        """Marry the love of your life!"""
        if not target:
            target_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            target_user = MarriageUser.get_user(ctx, target, cog=self)

        if not target_user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        if target_user.id == ctx.author.id:
            return await ctx.send("You cannot marry yourself!")

        author_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)

        if target_user.id in await author_user.spouses:
            return await ctx.send("You two are already married!")

        if not await self.config_manager.config.multi():
            if await author_user.married:
                return await ctx.send("You're already married!")
            elif await target_user.married:
                return await ctx.send("They're already married!")

        await ctx.send(
            f"{ctx.author.display_name} has asked {target_user.display_name} to marry them!\n"
            f"{target_user.mention}, what do you say?"
        )
        pred = CustomMessagePredicate.yes_or_no(ctx, ctx.channel, target_user)
        try:
            await self.bot.wait_for("message", timeout=self.CONSENT_TIMEOUT, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send(
                f"{target_user.display_name} took too long to respond. Try again later."
            )

        if not pred.result:
            return await ctx.send("Oh no... I was looking forward to the ceremony...")

        await author_user.marry(target_user)
        await target_user.marry(ctx.author)

        await ctx.send(
            f":church: {ctx.author.mention} and {target_user.mention} are now a happy married couple! Congrats! :tada:"
        )

    @commands.max_concurrency(1, commands.BucketType.channel, wait=True)
    @commands.guild_only()
    @commands.command()
    async def divorce(self, ctx: commands.Context, target: typing.Union[int, str]):
        """Divorce your current spouse"""
        if not target:
            target_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            target_user = MarriageUser.get_user(ctx, target, cog=self)

        if not target_user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        if target_user.id == ctx.author.id:
            return await ctx.send("You cannot divorce yourself!")

        author_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)

        # There's no need to ask for consent here as saying no will just result in the same outcome
        spouses = await author_user.spouses
        if not spouses or target_user.id not in spouses:
            return await ctx.send("You two aren't married!")

        await author_user.divorce(target_user)
        await target_user.divorce(ctx.author)

        await ctx.send(
            f":broken_heart: {ctx.author.mention} and {target_user.mention} got divorced! :broken_heart:"
        )

    @commands.max_concurrency(1, commands.BucketType.channel, wait=True)
    @commands.guild_only()
    @commands.command()
    async def perform(
        self,
        ctx: commands.Context,
        action_name: str,
        target: typing.Union[int, str],
    ):
        """Do something with someone."""
        if not target:
            target_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            target_user = MarriageUser.get_user(ctx, target, cog=self)

        if not target_user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        if target_user.id == ctx.author.id:
            return await ctx.send("You cannot perform anything with yourself!")

        if action_name not in self.actions.as_list():
            return await ctx.send(
                f"Available actions are: {humanize_list(self.actions.as_list())}"
            )

        action = self.actions.get(action_name)
        contentment = action.contentment
        description = action.description

        author_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)

        # check if the author is married and if the target is their spouse
        # remove half of the contentment if the target is not their spouse before
        # performing the action
        await self.check_contentment(ctx, target_user, contentment / 2)

        if action.require_consent:
            await ctx.send(
                action.consent_description.format(
                    author=ctx.author.display_name, target=target_user.mention
                )
            )
            pred = CustomMessagePredicate.yes_or_no(ctx, ctx.channel, target_user)
            try:
                await self.bot.wait_for(
                    "message", timeout=self.CONSENT_TIMEOUT, check=pred
                )
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"{target_user.display_name} took to long to respond. Try again later, please. (You didn't lose any contentment.)"
                )
            if not pred.result:
                await author_user.change_contentment(contentment * -1)
                return await ctx.send(
                    f"{target_user.display_name} does not wish to do that."
                )

        # At this point, either the target has given consent or the action didn't require it
        await ctx.send(
            description.format(author=ctx.author.mention, target=target_user.mention)
        )
        await target_user.change_contentment(contentment)
        await author_user.change_contentment(contentment)

        # remove the rest contentment after performing the action
        return await self.check_contentment(ctx, target_user, contentment / 2)

    @commands.guild_only()
    @commands.command()
    async def gift(
        self,
        ctx: commands.Context,
        gift_name: str,
        target: typing.Union[int, str],
    ):
        """Give someone something."""
        author_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        if not target:
            target_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)
        else:
            target_user = MarriageUser.get_user(ctx, target, cog=self)

        if not target_user:
            return await ctx.send(self.NONE_USER_MESSAGE.format(key=target))

        if target_user.id == ctx.author.id:
            return await ctx.send("You cannot give yourself a gift!")

        if gift_name not in self.gifts.as_list():
            return await ctx.send(
                f"Available gifts are: {humanize_list(self.gifts.as_list())}"
            )
        else:
            gift = self.gifts.get(gift_name)
            contentment = gift.contentment

        await author_user.modify_gifts(gift_name, -1, contentment)
        await target_user.modify_gifts(gift_name, 1, contentment)

        await ctx.send(
            gift.description.format(
                author=ctx.author.mention, item=gift_name, target=target_user.mention
            )
        )

        await self.check_contentment(ctx, target_user, contentment)

    async def check_contentment(self, ctx, user: discord.User, contentment: int):
        """Checks the contentment level of a member and handles divorce if necessary.

        This function checks if the author is married and if the target member is their spouse.
        If the target member is not their spouse and the contentment level is too low,
        the author and their spouses will divorce.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            member (discord.Member): The member whose contentment level is being checked.
            contentment (int): The threshold contentment level.

        Returns:
            None
        """
        author_user = MarriageUser(bot=self.bot, parent=self, user=ctx.author)

        # author isn't married, it's cool
        married = await author_user.married
        if not married:
            self.logger.debug("{author.display_name} isn't married")
            return

        # author is married, but the target is their spouse
        spouses = await author_user.spouses
        self.logger.debug(f"{author_user.display_name} Spouses: {spouses}")
        if user.id in spouses:
            self.logger.debug(f"{user.display_name} is their spouse")
            return

        # Uh oh, the target is not their spouse
        self.logger.debug("Author is cheating!")
        for spouse_id in spouses:
            spouse = MarriageUser(
                bot=self.bot, parent=self, user=self.bot.get_user(spouse_id)
            )
            self.logger.debug(f"Checking contentment for {spouse.display_name}")
            await spouse.change_contentment(contentment * -1)
            current_contentment = await spouse.contentment
            self.logger.debug(
                f"Contentment for {spouse.display_name} is now {current_contentment}"
            )
            if current_contentment <= 0:
                self.logger.debug(
                    f"Divorcing {spouse.display_name} & {author_user.display_name}"
                )
                await author_user.divorce(spouse)
                await spouse.divorce(author_user)
                await ctx.send(
                    f":broken_heart: {author_user.mention} has made {spouse.mention} completely unhappy with their actions so {spouse.display_name} has divorced them!"
                )
