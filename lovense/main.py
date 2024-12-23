import asyncio
import logging

import discord
from redbot.core import commands
from redbot.core.bot import Red

from . import __version__, __credits__, const
from .webserver import WebServer
from .toys import Patterns, Controller
from .guilds import Guilds


class LovenseCog(commands.Cog):
    """
    A Cog for managing Lovense devices within a Discord bot.

    Attributes:
        bot (commands.Bot): The bot instance.
        logger (logging.Logger): Logger for the cog.
        guilds (Guilds): Instance of the Guilds class.
        controller (Controller): Instance of the Controller class.
        callbacks (Webserver): Instance of the Webserver class.
    """

    def __init__(self, bot: commands.Bot = Red) -> None:
        """
        Initialize the Lovense cog.

        Args:
            bot (commands.Bot): The bot instance.
        """
        super().__init__()

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.bot = bot
        self.guilds = Guilds(self)
        self.controller = Controller(self)

        self.webserver = WebServer(callback=self.handle_data)
        self.bot.loop.create_task(self.webserver.run())
        self.bot.loop.create_task(self.update_activity())

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    def handle_data(self, data):
        """_summary_

        Args:
            data (_type_): _description_
        """
        """ The Lovense Remote app will send the following POST to your server:
        {
            "uid": "xxx",
            "appVersion": "4.0.3",
            "toys": {
                "xxxx": {
                "nickName": "",
                "name": "max",
                "id": "xxxx",
                "status": 1
                }
            },
            "wssPort": "34568",
            "httpPort": "34567",
            "wsPort": "34567",
            "appType": "remote",
            "domain": "192-168-1-44.lovense.club",
            "utoken": "xxxxxx",
            "httpsPort": "34568",
            "version": "101",
            "platform": "android"
        }
        """
        self.logger.debug(f"Parent received data: {data}")
        guild_id, user_id = data.get("uid").split(":")
        self.guilds.add_user(guild_id, user_id, data)

        # Add your logic to process the data here

    async def update_activity(self) -> None:
        """
        Update the bot's activity status.

        Waits until the bot is ready before updating the activity.
        """
        self.logger.info("Lovense activity update.")
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()

        toy_count = 0
        while True:
            last_count = toy_count
            toy_count = sum(
                [len(self.controller.get_toys(str(x))) for x in self.guilds.ids]
            )

            if toy_count != last_count:
                playing = "with " + (
                    "no toys"
                    if toy_count == 0
                    else "1 toy" if toy_count == 1 else "{} toys".format(toy_count)
                )
                self.logger.info(
                    "Toy count is now {}, was {}. Updating presence.".format(
                        toy_count, last_count
                    )
                )
                await self.bot.change_presence(activity=discord.Game(name=playing))

            await asyncio.sleep(60)

    @commands.group(invoke_without_command=True)
    async def lovense(self, ctx: commands.Context):
        """Parent group for lovense commands."""
        if ctx.invoked_subcommand is None:
            pass
            # return await self.helper.roleplay(ctx)

    @lovense.command()
    async def connect(self, ctx: commands.Context):
        """Connect a toy"""
        url = self.controller.get_connection_qr(str(ctx.guild.id), str(ctx.author.id))
        if url is None:
            await ctx.send("Sorry, I can't connect to Lovense right now.")
            return
        self.logger.debug(f"Lovense QC: {url}")
        embed = discord.Embed(
            title="Connect with Lovense Remote",
            description="""Using the Lovense Remote app, press the + button > Scan QR.
            
            This is *your* personal QR code. Sharing it might prevent the connection from working.""",
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @lovense.command()
    async def status(self, ctx: commands.Context):
        """List connected toys"""
        embed = discord.Embed(title="Connected Toys")
        toy_count = {}

        for toy in self.controller.get_toys(str(ctx.guild.id)):
            toy_count[toy] = toy_count + 1 if toy in toy_count else 1

        if not toy_count:
            await ctx.send("There are no toys connected")
            return

        for toy, count in toy_count.items():
            embed.add_field(
                name=toy.title(), value="{} connected".format(count), inline=True
            )

        await ctx.send(embed=embed)

    @lovense.command()
    async def vibrate(
        self, ctx: commands.Context, strength: int = 10, duration: int = 10
    ):
        """Vibrate all toys

        Args:
            strength (int): Vibration strength (1-20). Defaults to 10
            duration (int): Number of seconds it lasts. Defaults to 10 seconds
        """
        if self.controller.vibrate(ctx.guild.id, duration=duration, strength=strength):
            await ctx.send("Buzz buzz!")
        else:
            await ctx.send("There aren't any toys connected")

    @lovense.command()
    async def rotate(self, ctx: commands.Context, strength=10, duration=10):
        """Rotate all toys

        Args:
            ctx (commands.Context): _description_
            strength (int, optional): Rotation strength (1-20). Defaults to 10.
            duration (int, optional): Number of seconds it lasts. Defaults to 10 seconds.
        """
        if self.controller.rotate(ctx.guild.id, duration=duration, strength=strength):
            await ctx.send("You spin me right round baby...")
        else:
            await ctx.send("There aren't any toys connected")

    @lovense.command()
    async def pump(self, ctx: commands.Context, strength=2, duration=10):
        """Pump all toys

        Args:
            ctx (commands.Context): _description_
            strength (int, optional): Rotation strength (1-20). Defaults to 10.
            duration (int, optional): Number of seconds it lasts. Defaults to 10 seconds.
        """
        if self.controller.pump(ctx.guild.id, duration=duration, strength=strength):
            await ctx.send("Let's get pumped!")
        else:
            await ctx.send("There aren't any toys connected")

    @lovense.command()
    async def vibrate_pattern(self, ctx: commands.Context, pattern: Patterns):
        """Send a pattern to all toys. Loops until stopped, or replaced with another vibration or pattern.

        Args:
            pattern (str): The pattern to send
        """
        if self.controller.pattern(ctx.guild.id, pattern):
            await ctx.send("Here comes the {}!".format(pattern))
        else:
            await ctx.send("There aren't any toys connected")

    @lovense.command()
    async def stop(self, ctx: commands.Context):
        """Stop all toys"""
        if self.controller.stop(ctx.guild.id):
            await ctx.send("Break-time!")
        else:
            await ctx.send("There aren't any toys connected")
