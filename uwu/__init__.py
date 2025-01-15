"""Package for UwU cog."""

__author__ = "Unicornia Team"
__credits__ = ["Ruffiana", "Kirin", "Ruff", "PhasecoreX"]
__version__ = "2.2.1"
__license__ = "MIT"


import json
from pathlib import Path

from redbot.core.bot import Red

from .main import UwUCog

with Path(__file__).parent.joinpath("info.json").open() as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]


async def setup(bot: Red) -> None:
    """Load UwU cog."""
    await bot.add_cog(UwUCog(bot))
