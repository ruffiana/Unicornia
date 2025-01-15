"""ModHelper Cog"""

__version__ = "1.0.3"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana"]
__license__ = "MIT"


from .main import ModHelperCog


# Your bot's code continues here...
async def setup(bot):
    await bot.add_cog(ModHelperCog(bot))
