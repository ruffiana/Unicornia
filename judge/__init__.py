"""Template for redbot cog"""

__version__ = "1.1.1"
__author__ = "Ruffiana"

from .main import JudgeCog


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(JudgeCog(bot))
