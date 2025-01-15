"""
This is a heavily modified and refactored version of saurichable's "marriage" cog.

The source version can be found here:
https://github.com/elijabesu/SauriCogs/tree/master/marriage

Main focus has been on decoupling everything from the currency systems
"""

__version__ = "2.0.31"
__author__ = "Unicornia Team"
__credits__ = ["Ruffiana"]
__license__ = "MIT"

from .main import Marriage


async def setup(bot):
    await bot.add_cog(Marriage(bot))
