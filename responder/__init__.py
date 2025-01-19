"""Template for redbot cog"""

__version__ = "0.1.72"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana", "Radon"]
__license__ = "MIT"


from .main import ResponderCog


async def setup(bot):
    await bot.add_cog(ResponderCog(bot))
