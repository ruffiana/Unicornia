"""Template for redbot cog"""

__version__ = "1.0.0"

from .main import JudgesCog


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(JudgesCog(bot))
