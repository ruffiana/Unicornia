from redbot.core import commands
from redbot.core.bot import Red

from .config import ConfigManager


class Actions:
    DEFAULT = {
        "flirt": {
            "contentment": 5,
            "price": 0,
            "require_consent": False,
            "description": ":heart_eyes: {author} is flirting with {target}",
        },
        "fuck": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants to bang you, {target}, give consent?",
            "description": ":smirk: {author} banged {target} <a:letsfuck:964615340539670621>",
        },
        "suck": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants to suck you off, {target}, give consent?",
            "description": "<a:sucking:695495067376287744> {author} sucked off {target}",
        },
        "peg": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants to peg you, {target}, give consent?",
            "description": "<a:pegging:964615733390753822> {author} is pegging {target}",
        },
        "breed": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants to breed you, {target}, give consent?",
            "description": "<a:breed:993881108221526166> {author} is breeding {target}",
        },
        "siton": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants to sit on your face, {target}, give consent?",
            "description": "<a:sitonfacepov:993881131239866388> {author} is sitting on {target}'s face",
        },
        "capture": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants to do bad things to you, {target}, give consent?",
            "description": "<:caged:993883835131502726> {author} has captured {target} and put them in a cage :3",
        },
        "lock": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants put a chastity cage/belt on {target}, give consent?",
            "description": "<:chastity:993884363798364221> {author} has put a chastity device on {target} and locked it :3",
        },
        "collar": {
            "contentment": 5,
            "price": 0,
            "require_consent": True,
            "consent_description": "{author} wants collar {target}, give consent?",
            "description": "<:a_CollarAndLeash:993884751029076008> {author} has collared {target}. They are now on a leash :3",
        },
        "dinner": {
            "contentment": 15,
            "price": 0,
            "require_consent": False,
            "description": ":ramen: {author} took {target} on a fancy dinner",
        },
        "date": {
            "contentment": 10,
            "price": 0,
            "require_consent": False,
            "description": ":relaxed: {author} took {target} on a nice date",
        },
    }

    def __init__(self, bot: Red = None, parent=None):
        self.bot = bot
        self.parent = parent
        self.config_manager = (
            self.parent.config_manager
            if self.parent.config_manager
            else ConfigManager()
        )

    async def _get_actions(self, ctx: commands.Context):
        actions = list(self.DEFAULT.keys())

        conf = await self.config_manager.get_guild_config(ctx.guild)

        removed_actions = await conf.removed_actions()
        for removed in removed_actions:
            actions.remove(removed)

        custom_actions = await conf.custom_actions()
        custom_actions = list(custom_actions.keys()) if custom_actions else []
        actions.extend(custom_actions)

        return actions

    @property
    async def custom(self, ctx):
        conf = await self.config_manager.get_guild_config(ctx.guild)
        custom_actions = await conf.custom_actions()
        custom_actions = list(custom_actions.keys()) if custom_actions else []
        return custom_actions

    def is_custom(self, ctx, item):
        return item in self.custom

    @property
    async def removed(self, ctx):
        conf = await self.config_manager.get_guild_config(ctx.guild)
        removed_actions = await conf.removed_actions()
        return removed_actions

    async def is_removed(self, ctx, item):
        return item in await self.removed

    async def as_list(self, ctx):
        actions_keys = await self._get_actions(ctx)
        if not actions_keys:
            return "None"

        actions = ""

        for key in actions_keys:
            if key in self.custom:
                action = self.custom.get(key)
            elif key in self.DEFAULT:
                action = self.DEFAULT.get(key)
            else:
                f"{key} is not a custom or default action"
                continue

            contentment = action.get("contentment")
            price = action.get("price")
            actions += f"{key.capitalize()}: {contentment} contentment, {price} price\n"
