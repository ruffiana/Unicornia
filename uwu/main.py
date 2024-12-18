"""UwU cog for Red-DiscordBot by PhasecoreX.

I did not UwUize the docstrings in this module. You're welcome.
- Ruffiana
"""

import asyncio
import logging
import random
from contextlib import suppress
from typing import Any, ClassVar, Tuple

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils import common_filters

from . import __author__, __version__


class UwUCog(commands.Cog):
    """UwU."""

    KAOMOJI_JOY: ClassVar[list[str]] = [
        " (\\* ^ ω ^)",
        " (o^▽^o)",
        " (≧◡≦)",
        ' ☆⌒ヽ(\\*"､^\\*)chu',
        " ( ˘⌣˘)♡(˘⌣˘ )",
        " xD",
    ]
    KAOMOJI_EMBARRASSED: ClassVar[list[str]] = [
        " (/ />/ ▽ /</ /)..",
        " (\\*^.^\\*)..,",
        "..,",
        ",,,",
        "... ",
        ".. ",
        " mmm..",
        "O.o",
    ]
    KAOMOJI_CONFUSE: ClassVar[list[str]] = [
        " (o_O)?",
        " (°ロ°) !?",
        " (ーー;)?",
        " owo?",
    ]
    KAOMOJI_SPARKLES: ClassVar[list[str]] = [
        " \\*:･ﾟ✧\\*:･ﾟ✧ ",
        " ☆\\*:・ﾟ ",
        "〜☆ ",
        " uguu.., ",
        "-.-",
    ]

    # Replacments for final punctuation
    PUNCTUATION = {
        ".": KAOMOJI_JOY,
        "?": KAOMOJI_CONFUSE,
        "!": KAOMOJI_JOY,
        ",": KAOMOJI_EMBARRASSED,
    }
    # Chance for punctuation to be replaced as %.
    # Default should be 25
    PUNCTUATION_CHANCE = {".": 33, "?": 50, "!": 50, ",": 33}

    # Full word replacements
    WORDS = {
        "you're": "ur",
        "youre": "ur",
        "fuck": "fwickk",
        "shit": "poopoo",
        "bitch": "meanie",
        "asshole": "b-butthole",
        "dick": "peenie",
        "penis": "cwitty",
        "cum": "cummies",
        "semen": "cummies",
        "ass": "b-butt",
        "dad": "daddy",
        "father": "daddy",
    }

    # syllable replacements
    SYLLABLES = {
        "l": "w",
        "r": "w",
        "na": "nya",
        "ne": "nye",
        "ni": "nyi",
        "no": "nyo",
        "nu": "nyu",
        "ove": "uv",
    }

    # preserve these word endings for readability
    ENDINGS = ["le", "ll", "er", "re", "les", "lls", "ers", "res"]

    def __init__(self, bot: commands.Bot = Red):
        self.bot: commands.Bot = bot

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )
        self.logger.setLevel(logging.DEBUG)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Show version in help."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {__version__}"

    async def red_delete_data_for_user(self, *, _requester: str, _user_id: int) -> None:
        """Nothing to delete."""
        return

    @commands.command(aliases=["owo"])
    async def uwu(self, ctx: commands.Context, *, text: str | None = None) -> None:
        """UwUize the replied to message, previous message, or your own text."""
        if text:
            return await self.send_uwu_message(ctx, text)

        # Check if the message is a reply and the referenced message was written by the invoker
        if ctx.message.reference:
            with suppress(discord.Forbidden, discord.NotFound, discord.HTTPException):
                message_id = ctx.message.reference.message_id
                if message_id:
                    referenced_message = await ctx.fetch_message(message_id)
                    if referenced_message.author == ctx.author:
                        return await self.send_uwu_message(
                            ctx, referenced_message.content
                        )
                    else:
                        return await self.send_uwu_message(
                            ctx,
                            f"I can only translate messages from you {ctx.author.display_name}.",
                        )

        # Find the previous message written by the invoker
        message = await self.get_previous_message(ctx)
        if message:
            return await self.send_uwu_message(ctx, message.content, message=message)

        # If no appropriate message is found
        await self.send_uwu_message(ctx, "I can't translate that!", message=ctx.message)

    async def get_previous_message(self, ctx):
        messages = [message async for message in ctx.channel.history(limit=10)]
        for message in messages:
            if message.author != ctx.author:
                continue
            if message.content.lower().startswith("&uwu"):
                continue
            return message

    async def send_uwu_message(
        self, ctx: commands.Context, text: str, message: discord.Message = None
    ) -> None:
        """Send the UwUized message."""
        uwu = self.translate(text)

        await self.type_message(
            ctx.channel,
            uwu,
            message=message,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=False, roles=False
            ),
        )

    def translate(self, string: str) -> str:
        """
        Convert a given string by "UwUizing" each word.

        This method processes the input string character by character. It groups
        characters into words, applies the 'UwUize' transformation to each word
        using the `UwUize_word` method, and then reassembles the string. Non-printable
        characters and spaces are added to the resulting string without modification.

        Args:
            string (str): The input string to be "UwUized".

        Returns:
            str: The transformed string with each word "UwUized".
        """
        converted = []
        current_word = []

        for letter in string:
            if letter.isprintable() and not letter.isspace():
                current_word.append(letter)
            else:
                if current_word:
                    converted.append(self.translate_word("".join(current_word)))
                    current_word = []
                converted.append(letter)

        if current_word:
            converted.append(self.translate_word("".join(current_word)))

        return "".join(converted)

    def separate_punctuation(self, word: str) -> Tuple[str, str]:
        """Get the final punctuation of a word, if it exists."""
        final_punctuation = ""
        # don't use string.punctuation here.
        if word and word[-1] in self.PUNCTUATION.keys():
            final_punctuation = word[-1]
            word = word[:-1]
        return word, final_punctuation

    def apply_word_exceptions(self, word: str, words_dict: dict) -> str:
        """Apply full word exceptions using a dictionary lookup."""
        return words_dict.get(word, word)

    def convert_syllables(self, word: str) -> str:
        """Convert word syllables using a dictionary and protect specific word endings."""
        protected = ""
        for ending in self.ENDINGS:
            if word.endswith(ending):
                protected = word[-len(ending) :]
                word = word[: -len(ending)]
                break

        for syllable, replacement in self.SYLLABLES.items():
            word = word.replace(syllable, replacement)

        return f"{word}{protected}"

    def add_stutter(self, word: str) -> str:
        """Add occasional stutter to the word."""
        if (
            len(word) > 2
            and word[0].isalpha()
            and "-" not in word
            and not random.randint(0, 6)
        ):
            word = f"{word[0]}-{word}"
        return word

    def convert_punctuation(self, punctuation: str) -> str:
        """Process punctuation with a chance to be replaced with a kaomoji."""
        # get chance to proc from dict. Default is 25%
        chance = self.PUNCTUATION_CHANCE.get(punctuation, 25)
        if random.randint(1, 100) <= chance:
            replacement = random.choice(
                self.PUNCTUATION.get(punctuation, self.KAOMOJI_SPARKLES)
            )
            self.logger.debug(f"Replaced {punctuation} with {replacement}")
            return replacement
        else:
            return punctuation

    def translate_word(self, word: str) -> str:
        """
        UwUize and return a word.

        This function transforms the given word by applying a series of modifications:
        1. Converts the word to lowercase.
        2. Separates the word from any final punctuation.
        3. Checks for full word exceptions and replaces them if found.
        4. Protects specific word endings from being changed.
        5. Converts syllables based on predefined mappings.
        6. Adds occasional stutter to the word.
        7. Processes the final punctuation with a chance to replace it with a kaomoji.

        Args:
            word (str): The input word to UwUize.

        Returns:
            str: The transformed word with all modifications applied.
        """
        word = word.lower()

        # Get the final punctuation if it exists
        word, final_punctuation = self.separate_punctuation(word)

        # Apply word exceptions
        uwu = self.apply_word_exceptions(word, self.WORDS)

        if (
            uwu == word
        ):  # Proceed with normal word conversion only if no exception was found
            # Convert word syllables and protect specific word endings
            uwu = self.convert_syllables(uwu)

        # Add occasional stutter
        uwu = self.add_stutter(uwu)

        # Process punctuation
        if final_punctuation:
            final_punctuation = self.convert_punctuation(final_punctuation)

        # Add back punctuations and return
        return f"{uwu}{final_punctuation}"

    async def type_message(
        self,
        destination: discord.abc.Messageable,
        content: str,
        message: discord.Message,
        **kwargs: Any,
    ) -> discord.Message | None:
        """Simulate typing and sending a message to a destination.

        Will send a typing indicator, wait a variable amount of time based on the length
        of the text (to simulate typing speed), then send the message.
        """
        content = common_filters.filter_urls(content)
        with suppress(discord.HTTPException):
            async with destination.typing():
                await asyncio.sleep(max(0.25, min(2.5, len(content) * 0.01)))
            if message:
                return await message.reply(content=content, **kwargs)
            else:
                return await destination.send(content=content, **kwargs)
