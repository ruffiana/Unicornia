class Cookies:
    def __init__(self, bot, parent=None):
        self.bot = bot
        self.parent = parent

    async def _get_cookies(self, user):
        return await self.bot.get_cog("Cookies").get_cookies(user)

    async def _can_spend_cookies(self, user, amount):
        return bool(await self.bot.get_cog("Cookies").can_spend(user, amount))

    async def _withdraw_cookies(self, user, amount):
        return await self.bot.get_cog("Cookies").withdraw_cookies(user, amount)

    async def _deposit_cookies(self, user, amount):
        return await self.bot.get_cog("Cookies").deposit_cookies(user, amount)
