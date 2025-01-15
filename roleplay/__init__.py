"""RedBot cog for roleplay

TODO:
    Add "ask" command
"""

__version__ = "2.5.42"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana", "the.kirin", "neviyn", "fitz.lol"]

from .main import Roleplay


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(Roleplay(bot))
