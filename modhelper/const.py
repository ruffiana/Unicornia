import logging

from discord import Color

from . import __version__, __author__

LOGGER_LEVEL = logging.INFO

# Some constants used for consistency when making embeds
EMBED_LIST_LIMIT = 25
EMBED_COLOR = Color.from_str("#9401fe")
EMBED_FOOTER = f"ModHelper Cog ({__version__}) - by: {__author__}"
