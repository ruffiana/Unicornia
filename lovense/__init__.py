"""Refactor of chmod-000 "LovenseBot" as a cog for redbfot

https://github.com/chmod-000
"""

__version__ = "1.0.0"
__author__ = "ruffiana"
__credits__ = ["chmod-000"]

from .main import LovenseCog


async def setup(bot):
    await bot.add_cog(LovenseCog(bot))
