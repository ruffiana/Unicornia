"""Cutie of the Month Contest Cog"""

__version__ = "1.0.12"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana"]
__license__ = "MIT"

from .main import ContestCog


async def setup(bot):
    await bot.add_cog(ContestCog(bot))
