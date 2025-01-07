import asyncio

from redbot.core import Config, commands
from redbot.core.bot import Red


class ConfigManager(commands.Cog):
    """Manages config data"""

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
        "gifts": {
            # "gift": owned pcs
        },
    }

    def __init__(self, bot: Red, parent=None):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=5465461324979524, force_registration=True
        )

        self.config.register_guild(
            toggle=False,
            marprice=1500,
            divprice=2,
            currency=0,
            multi=False,
            custom_actions={},
            custom_gifts={},
            removed_actions=[],
            removed_gifts=[],
            gift_text=":gift: {author} has gifted one {item} to {target}",
        )

        self.config.register_global(
            is_global=False,
            toggle=False,
            marprice=1500,
            divprice=2,
            currency=0,
            multi=False,
            custom_actions={},
            custom_gifts={},
            removed_actions=[],
            removed_gifts=[],
            gift_text=":gift: {author} has gifted one {item} to {target}",
        )

        self.config.register_member(**self.DEFAULT_USER)
        self.config.register_user(**self.DEFAULT_USER)

    async def init_post_read(self, ctx):
        self.config_manager = (
            self.parent.config_manager
            if self.parent.config_manager
            else ConfigManager()
        )

    async def red_delete_data_for_user(self, *, requester, user_id):
        await self.config.user_from_id(user_id).clear()
        for guild in self.bot.guilds:
            await self.config.member_from_ids(guild.id, user_id).clear()
            for member in guild.members:
                member_exes = await self.config.member(member).exes()
                member_spouses = await self.config.member(member).spouses()
                if user_id in member_exes:
                    member_exes.remove(user_id)
                    await self.config.member(member).exes.set(member_exes)
                if user_id in member_spouses:
                    member_spouses.remove(user_id)
                    if len(member_spouses) == 0:
                        await self.config.member(member).married.set(False)
                    await self.config.member(member).spouses.set(member_spouses)

    async def get_guild_config(self, guild):
        return (
            self.config if await self.config.is_global() else self.config.guild(guild)
        )

    async def get_user_config(self, user):
        return (
            self.config.user(user)
            if await self.config.is_global()
            else self.config.member(user)
        )

    async def _get_user_conf_group(self):
        return self.config.user if await self.config.is_global() else self.config.member
