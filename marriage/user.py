import logging
import typing
from redbot.core import commands

import discord
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list


class MarriageUser:
    """Wraps discord.User to add marriage data and user config management"""

    DEFAULT_USER = {
        "married": False,
        "current": [],
        "divorced": False,
        "exes": [],
        "about": "I'm mysterious.",
        "crush": None,
        "marcount": 0,
        "dircount": 0,
        "contentment": 100,
        "gifts": {},  # {gift_name: amount}
    }

    def __init__(self, bot: Red, parent: None, user: discord.User):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        self.bot = bot
        self.parent = parent
        self.user = user

        # Copy all attributes from discord.User to this class for direct access to them
        # ex. [MarriageUser].name, [MarriageUser].id, etc.
        for attr in dir(user):
            if not attr.startswith("_") and not hasattr(self, attr):
                # this logger adds a lot of debug spam to the console.
                # Uncomment only if needed
                # self.logger.debug(f"Setting attribute {attr}")
                setattr(self, attr, getattr(user, attr))

        # use the config_manager object instantiated in parent class
        self.config_manager = parent.config_manager
        self.config = self.config_manager.config
        self.logger.debug(f"Config manager: {self.config_manager}")

    @classmethod
    def get_user(cls, ctx, user_key: typing.Union[int, str], cog: commands.Cog):
        """Gets a user from various types

        Args:
            ctx (commands.Context): The context of the command invocation.
            user_key (Union[int, str]): The ID, username, or mention of the user to be
            added to the group.
            cog (commands.Cog): The cog that is calling this method.

        Returns:
           MarriageUser
        """
        user = None
        if isinstance(user_key, int):
            user = cog.bot.get_user(user_key)
        elif isinstance(user_key, str):
            # Check for mention format
            if user_key.startswith("<@") and user_key.endswith(">"):
                user_id = int(user_key[2:-1])
                user = cog.bot.get_user(user_id)
            else:
                # get a list of members to search through. If ctx.guild.members is valid
                # then we're in a server channel. Otherwise, we're in a direct message
                # and use .get_all_members() to ge a generator with every discord.Member
                # the Discord client can see
                member = None
                try:
                    members = ctx.guild.members
                except AttributeError:
                    members = cog.bot.get_all_members()
                # Search through list of members for a user using their global username
                # or display name
                for guild_member in members:
                    if (
                        guild_member.name == user_key
                        or guild_member.display_name == user_key
                    ):
                        member = guild_member
                        break
                # if we found a member, get the user object
                if member:
                    user = cog.bot.get_user(member.id)

        if user is None:
            cog.logger.warning(f'Unable to find user using "{user_key}".')
            return None
        else:
            cog.logger.debug(
                f"Found {user.display_name} ({user.id}) using {user_key} as key."
            )
            return MarriageUser(cog.bot, cog, user)

    @property
    async def relationship_status(self):
        married = await self.married
        divorced = await self.divorced
        self.logger.debug(f"married: {married}, divorced: {divorced}")
        if married:
            return "Married"
        elif divorced:
            return "Divorced"
        else:
            return "Single"

    @property
    async def married(self) -> bool:
        return await self.config.user(self.user).married()

    async def set_married(self, value: bool):
        return await self.config.user(self.user).married.set(value)

    @property
    async def marriage_count(self) -> int:
        marriage_count = await self.config.user(self.user).marcount()
        return int(marriage_count)

    async def _set_marriage_count(self, value: int):
        await self.config.user(self.user).marcount.set(value)

    async def change_marriage_count(self, value: int):
        current_marriage_count = await self.marriage_count
        value = max(0, value + current_marriage_count)
        await self._set_marriage_count(value)

    async def marry(self, user: discord.User):
        await self.set_married(True)
        await self.change_marriage_count(1)
        await self.set_divorced(False)
        await self.add_spouse(user)
        # getting married is a happy event, so we increase contentment by +50
        await self.change_contentment(50)

    @property
    async def divorced(self) -> bool:
        return await self.config.user(self.user).divorced()

    async def set_divorced(self, value: bool):
        await self.config.user(self.user).divorced.set(value)

    @property
    async def divorce_count(self):
        divorce_count = await self.config.user(self.user).dircount()
        return int(divorce_count)

    async def _set_divorce_count(self, value):
        await self.config.user(self.user).dircount.set(value)

    async def change_divorce_count(self, value: int):
        current_divorce_count = await self.marriage_count
        value = max(0, value + current_divorce_count)
        await self._set_divorce_count(value)

    async def divorce(self, user: discord.User):
        await self.set_married(False)
        await self.remove_spouse(user)
        await self.set_divorced(True)
        await self.add_ex(user)
        # divorcing someone is a big deal, so we'll reduce contentment to 25
        await self._set_contentment(25)
        await self.change_divorce_count(1)

    @property
    async def spouses(self) -> list:
        spouses = await self.config.user(self.user).current()
        return spouses

    async def _set_spouses(self, value: list):
        await self.config.user(self.user).current.set(value)

    async def add_spouse(self, user: discord.User):
        async with self.config.user(self.user).current() as current_spouses:
            spouses = list(set(current_spouses + [user.id]))
            await self._set_spouses(spouses)

    async def remove_spouse(self, user: discord.User):
        async with self.config.user(self.user).current() as current_spouses:
            current_spouses.remove(user.id)

    async def spouses_as_list(self) -> list:
        spouses = await self.spouses
        if not spouses:
            return []
        else:
            return [self.bot.get_user(spouse_id).display_name for spouse_id in spouses]

    async def spouses_as_text(self) -> str:
        spouses = await self.spouses_as_list()
        if spouses:
            return humanize_list(spouses)
        else:
            return "None"

    @property
    async def exes(self) -> list:
        exes = await self.config.user(self.user).exes()
        return exes

    async def _set_exes(self, value):
        self.config.user(self.user).exes.set(value)

    async def add_ex(self, user: discord.User):
        async with self.config.user(self.user).exes() as current_exes:
            exes = list(set(current_exes + [user.id]))
            await self._set_exes(exes)

    async def remove_ex(self, user: discord.User):
        async with self.config.user(self.user).exes() as exes:
            exes.remove(user.id)

    async def exes_as_list(self) -> list:
        exes = await self.exes
        self.logger.debug(f"Exes: {exes}")
        if not exes:
            return []
        else:
            return [self.bot.get_user(ex_id).display_name for ex_id in exes]

    async def exes_as_text(self) -> str:
        exes = await self.exes_as_list()
        if exes:
            return humanize_list(exes)
        else:
            return "None"

    @property
    async def about(self) -> str:
        return await self.config.user(self.user).about()

    async def set_about(self, value: str):
        await self.config.user(self.user).about.set(value)

    @property
    async def crush(self) -> discord.User:
        crush = await self.config.user(self.user).crush()
        if crush:
            return self.bot.get_user(crush).display_name
        else:
            return "None"

    async def set_crush(self, user: discord.User):
        await self.config.user(self.user).crush.set(user.id)

    async def remove_crush(self):
        await self.config.user(self.user).crush.clear()

    @property
    async def contentment(self) -> int:
        contentment = await self.config.user(self.user).contentment()
        return int(contentment)

    async def _set_contentment(self, value: int):
        await self.config.user(self.user).contentment.set(value)

    async def change_contentment(self, value: int):
        current_contentment = await self.contentment
        value = max(0, min(100, value + current_contentment))
        await self._set_contentment(value)

    @property
    async def gifts(self) -> dict:
        return await self.config.user(self.user).gifts()

    async def set_gifts(self, gifts: dict):
        return await self.config.user(self.user).gifts.set(gifts)

    async def modify_gifts(self, gift_name: str, amount: int, contentment: int):
        async with self.config.user(self.user).gifts() as gifts:
            cur_amount = gifts.get(gift_name, 0)
            gifts[gift_name] = max(0, cur_amount + amount)
            await self.change_contentment(contentment)

    async def gifts_as_list(self):
        gifts = await self.gifts
        if not gifts:
            return []

        return [
            f'{gift} - {amount} {"pc" if amount == 1 else "pcs"}'
            for gift, amount in gifts.items()
            if amount > 0
        ]

    async def gifts_as_text(self):
        gifts = await self.gifts_as_list()
        self.logger.debug(f"Gifts: {gifts}")
        if gifts:
            return humanize_list(gifts)
        else:
            return "None"
