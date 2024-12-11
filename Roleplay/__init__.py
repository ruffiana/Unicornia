"""RedBot cog for roleplay"""

__version__ = "2.2.3"


from .roleplay import Roleplay


async def setup(bot):
    await bot.add_cog(Roleplay(bot))
