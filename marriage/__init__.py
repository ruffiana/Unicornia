"""
This is a heavily modified and refactored version of saurichable's "marriage" cog.

The source version can be found here:
https://github.com/elijabesu/SauriCogs/tree/master/marriage

Main focus has been on decoupling everything from the currency systems
"""

__version__ = "1.7.0"


from asyncio import create_task

from .main import Marriage


async def setup_after_ready(bot):
    await bot.wait_until_red_ready()
    cog = Marriage(bot)
    for name, command in cog.all_commands.items():
        if not command.parent:
            if bot.get_command(name):
                command.name = f"m{command.name}"
            for alias in command.aliases:
                if bot.get_command(alias):
                    command.aliases[command.aliases.index(alias)] = f"m{alias}"
    await bot.add_cog(cog)


async def setup(bot):
    create_task(setup_after_ready(bot))
