"""Refactor of chmod-000 "LovenseBot" as a cog for redbfot

https://github.com/chmod-000
"""

__version__ = "0.1.0"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana", "chmod-000"]
__license__ = "MIT"


from .main import LovenseCog


async def setup(bot):
    await bot.add_cog(LovenseCog(bot))
