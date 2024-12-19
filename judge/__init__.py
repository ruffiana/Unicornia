"""Template for redbot cog"""

__version__ = "0.2.0-alpha"
__author__ = "Ruffiana"

from .main import JudgesCog


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(JudgesCog(bot))
