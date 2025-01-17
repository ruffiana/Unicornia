"""Template for redbot cog"""

__version__ = "1.0.11"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana"]
__license__ = "MIT"


from .main import ResponderCog


async def setup(bot):
    await bot.add_cog(ResponderCog(bot))
