"""RedBot cog for roleplay

TODO:
    Add "ask" command
"""

__version__ = "2.5.1"
__author__ = "ruffiana"
__credits__ = ["the.kirin", "neviyn", "fitz.lol"]

from .main import Roleplay


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(Roleplay(bot))
