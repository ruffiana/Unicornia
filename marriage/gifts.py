from redbot.core import commands
from redbot.core.bot import Red

from .config import ConfigManager


class Gifts:
    DEFAULT = {
        "flower": {"contentment": 5, "price": 5},
        "sweets": {"contentment": 5, "price": 5},
        "alcohol": {"contentment": 5, "price": 5},
        "loveletter": {"contentment": 5, "price": 1},
        "food": {"contentment": 5, "price": 10},
        "makeup": {"contentment": 5, "price": 20},
        "car": {"contentment": 15, "price": 500},
        "yacht": {"contentment": 30, "price": 1000},
        "house": {"contentment": 60, "price": 25000},
    }

    def __init__(self, bot: Red = None, parent=None):
        self.bot = bot
        self.parent = parent
        self.config_manager = (
            self.parent.config_manager
            if self.parent.config_manager
            else ConfigManager()
        )

    async def _get_gifts(self, ctx: commands.Context):
        conf = await self.config_manager.get_guild_config(ctx.guild)

        gifts = list(self.DEFAULT.keys())

        removed_gifts = await self.removed
        for removed in removed_gifts:
            gifts.remove(removed)

        custom_gifts = self.custom
        gifts.extend(custom_gifts)

        return gifts

    @property
    async def custom(self, ctx):
        conf = await self.config_manager.get_guild_config(ctx.guild)
        custom_gifts = await conf.custom_gifts()
        custom_gifts = list(custom_gifts.keys()) if custom_gifts else []
        return custom_gifts

    def is_custom(self, ctx, item):
        return item in self.customW

    @property
    async def removed(self, ctx):
        conf = await self.config_manager.get_guild_config(ctx.guild)
        removed_gifts = await conf.removed_gifts()
        return removed_gifts

    async def is_removed(self, ctx, item):
        return item in await self.removed

    async def as_list(self, ctx):
        gifts_keys = await self._get_gifts(ctx)

        gifts = ""

        if not gifts_keys:
            return "None"

        for key in gifts_keys:
            if key in self.custom:
                gift = self.custom.get(key)
            elif key in self.DEFAULT:
                gift = self.DEFAULT.get(key)
            else:
                f"{key} is not a custom or default gift"
                continue

            contentment = gift.get("contentment")
            price = gift.get("price")
            gifts += f"{key.capitalize()}: {contentment} contentment, {price} price\n"
