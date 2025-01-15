import logging
from typing import Union

from redbot.core import Config, commands
from redbot.core.bot import Red

from .marriage_user import MarriageUser


class ConfigManager:
    """Manages global and user config data"""

    def __init__(self, bot: Red, parent: commands.Cog):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        self.bot = bot
        self.parent = parent

        self.config = Config.get_conf(
            self,
            identifier=self.parent.COG_IDENTIFIER,
            force_registration=True,
            # Need this to make sure the config data folder gets created under the cog name
            cog_name=self.parent.__class__.__name__,
        )

        self.config.register_global(
            toggle=False,
            multi=False,
        )
        self.config.register_user(**MarriageUser.DEFAULT_USER)

    def get_config_filepath(self) -> str:
        """Returns the local file path to where config data is saved."""
        return self.config._config_file

    async def init_post_read(self):
        self.config_manager = (
            self.parent.config_manager
            if self.parent.config_manager
            else ConfigManager()
        )

    @property
    async def multiple_spouses(self):
        return await self.config.multi()

    async def set_multiple_spouses(self, value: bool):
        await self.config.multi.set(value)
