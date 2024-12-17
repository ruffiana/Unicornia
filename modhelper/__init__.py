"""
ModHelper Cog

This module contains the ModHelper class, which provides commands to assist with
moderation tasks in a Discord server.

Commands:
    Find: The find command uses fuzzy matching to search for users by their username
    or display name.
"""

__version__ = "1.0.0"
__author__ = "Ruffiana"

from .main import ModHelper


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(ModHelper(bot))
