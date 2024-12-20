"""Template for redbot cog"""

__version__ = "0.3.0-alpha"
__author__ = "Ruffiana"

from .main import JudgeCog


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(JudgeCog(bot))
