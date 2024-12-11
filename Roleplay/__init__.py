"""RedBot cog for roleplay"""

__version__ = "2.2.2"


from .roleplay import Roleplay


async def setup(bot):
    await bot.add_cog(Roleplay(bot))
