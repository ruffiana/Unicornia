"""RedBot cog for roleplay

TODO:
    Add "ask" command
"""

__version__ = "2.3.1"
__author__ = "ruffiana"
__credits__ = ["the.kirin", "neviyn", "fitz.lol"]

import logging
from .main import Roleplay
from . import const

# # Set up logging
# logging.basicConfig(level=const.LOGGER_LEVEL)
# logger = logging.getLogger("redbot")
# logger.setLevel(const.LOGGER_LEVEL)


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(Roleplay(bot))
