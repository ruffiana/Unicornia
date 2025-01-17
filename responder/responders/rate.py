import re

import discord
from redbot.core.bot import Red

from ..unicornia import strings, web
from .rate_base import RateBase
from .text_responder_base import TextResponderBase
import random

IGNORE_WORDS = [
    "separate",
    "celebrate",
    "operate",
    "generate",
    "integrate",
    "moderate",
    "accelerate",
    "concentrate",
    "collaborate",
    "demonstrate",
    "elaborate",
    "illustrate",
    "incorporate",
    "liberate",
    "migrate",
    "narrate",
    "penetrate",
    "radiate",
    "saturate",
]


class GayRate(RateBase):
    title = "❯ Not Gay"
    description = "{target} is {rating}% Gay"
    thumbnail = r"https://cdn.discordapp.com/emojis/1088555199146242248.webp?size=128&quality=lossless"

    user_overrides: dict = {
        140186220255903746: {  # Kirin#9329
            "title": "❯ The Gay",
            "description": "❯ {target} is the gay.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/817150384111616011.webp?size=128&quality=lossless",
        },
        240942922285973506: {  # Emma#6688
            "title": "❯ Super Gay",
            "description": "❯ {target} is Super Duper Gay.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/817150384111616011.webp?size=128&quality=lossless",
        },
        144523162044858368: {
            "title": "❯ Super Gay",
            "description": "❯ {target} is 99.999% Gay.",
            "thumbnail": r"https://cdn.discordapp.com/emojis/1088555199146242248.webp?size=128&quality=lossless",
        },
    }

    rating_overrides = {
        90: {"title": "❯ Super Gay"},
        80: {"title": "❯ Extremely Gay"},
        70: {"title": "❯ Very Gay"},
        60: {"title": "❯ Quite Gay"},
        50: {"title": "❯ Definitely Gay"},
        40: {"title": "❯ Fairly Gay"},
        30: {"title": "❯ Pretty Gay"},
        20: {"title": "❯ Somewhat Gay"},
        10: {"title": "❯ Kinda Gay"},
        5: {"title": "❯ Slightly Gay"},
    }

    def __init__(self, parent, bot: Red):
        super().__init__(parent, bot)
        self.parent = parent
        self.bot = bot


class EmmaRate(RateBase):
    title = "❯ Emma Rate"
    description: str = "❯ {target} is {rating}% Emma"

    user_overrides: dict = {
        532750893326663681: {  # Emma#8765
            "description": "❯ {target} is an Emma! Also, not in charge.",
            # "thumbnail": r"https://cdn.discordapp.com/avatars/500690884028006420/6bded3f7b343bb8dbec99268f9b84801.png?size=1024",
        },
        240942922285973506: {  # Emma#6688
            "description": "❯ {target} is *the* Emma!",
        },
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)


class DimboRate(RateBase):
    title = "❯ Dimbo Rate"
    description = "{target} is {rating}% Dimbo"

    dimbo_defaults = {
        "title": "ERROR_CODE_4",
        "color": 16711680,
        "description": "User is too DIMBO to calculate.",
    }

    user_overrides = {
        532750893326663681: {  # Emma#8765
            "description": "❯ {target} is the Dimbo! \nAlso not in charge.",
            # "thumbnail": r"https://cdn.discordapp.com/attachments/686096388018405408/765924143279112252/dimbo.png?size=1024&quality=lossless",
        },
        1032686173849653425: dimbo_defaults,
        614500671147999233: dimbo_defaults,
        1110256621524885586: dimbo_defaults,
        14018622025590374: dimbo_defaults,
        474075064069783552: dimbo_defaults,
    }

    rating_overrides = {
        90: {
            "title": "❯ Like...Totally Dimbo",
            # "thumbnail": r"https://cdn.discordapp.com/attachments/686096388018405408/765924132822319114/dimbo3.png?size=1024&quality=lossless",
        },
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)


# class DomRate(RateBase):
#     title = "❯ {target} is 1000% mysterious..."
#     description = "Calculating dominance..."
#     thumbnail = r"https://cdn.discordapp.com/emojis/828672418318778398.gif?size=128&quality=lossless"
#     footer = "Results scientifically calculated based on member roles."

#     user_overrides = {
#         89582933735665664: {
#             "title": "❯ Dominant",
#             "description": "❯ {member.display_name} is 666% Dominant.",
#             "thumbnail": "https://cdn.discordapp.com/emojis/695147901407592499.webp?size=128&quality=lossless",
#         },
#         140186220255903746: {
#             "title": "❯ Submissive",
#             "description": "❯ {member.display_name} is 690% Submissive.",
#             "thumbnail": "https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
#         },
#         819276102325239840: {
#             "title": "❯ Submissive",
#             "description": "❯ {member.display_name} is 869% Submissive.",
#             "thumbnail": "https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
#         },
#         1058458210060751039: {
#             "title": "❯ Submissive",
#             "description": "❯ {member.display_name} is 555% Submissive.",
#             "thumbnail": "https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless",
#         },
#     }

#     def __init__(self, parent, bot: Red):
#         self.parent = parent
#         self.bot = bot
#         super().__init__(parent, bot)

#     @staticmethod
#     def get_rating(member: discord.Member):
#         SUB_ROLES = {
#             686097362107498504: 1.00,
#             768103786119823380: 0.75,
#             768103783498121296: 0.75,
#             694788843207131246: 1.00,
#             694788849020305451: 0.75,
#             694788851155337236: 0.20,
#             694788853419999352: 0.20,
#             694788854942531607: 0.50,
#             1074675006006644736: 0.05,
#             696082750775492688: 0.20,
#             694790765460848701: 1.00,
#             696048918248554627: 1.00,
#             708022873058574396: 0.25,
#             686098506834116620: 0.05,
#             686098381214711837: 1.00,
#         }

#         DOM_ROLES = {
#             686097057190379537: 1.00,
#             686097106083119115: 1.00,
#             694788857371033640: 1.00,
#             694788859015462923: 0.25,
#             694788860760031243: 0.25,
#             694789801353805862: 0.25,
#             694789803153162290: 0.25,
#             694790101095546890: 0.25,
#             694790104044142612: 1.00,
#             694790108230189087: 0.25,
#             686098541831127048: 0.10,
#             811471307106942996: 0.50,
#         }

#         # dom_total = sum(DOM_ROLES.values())
#         # sub_total = sum(SUB_ROLES.values())

#         dom_rating = sum(
#             value
#             for role, value in DOM_ROLES.items()
#             if role in [r.id for r in member.roles]
#         )
#         sub_rating = sum(
#             value
#             for role, value in SUB_ROLES.items()
#             if role in [r.id for r in member.roles]
#         )

#         rating = dom_rating - sub_rating

#         return rating

#     @classmethod
#     def get_description(cls, property, target, rating):
#         if rating > 0.0:
#             title = "❯ Dominant"
#             description = "{target} is {rating}% Dominant."
#             thumbnail = r"https://cdn.discordapp.com/emojis/695147901407592499.webp?size=128&quality=lossless"
#         elif rating < 0.0:
#             title = "❯ Submissive"
#             description = "{target} is {rating}% Submissive."
#             thumbnail = r"https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless"
#         else:
#             title = "❯ ???"
#             description = "{target} is 1000% mysterious..."
#             thumbnail = r"https://cdn.discordapp.com/emojis/828672418318778398.gif?size=128&quality=lossless"

#     @classmethod
#     async def respond(cls, message: discord.Message, target: discord.Member = None):
#         rating = cls.get_rating()

#         title = cls.get_title(target, rating)
#         description = cls.get_description(target, rating)
#         footer = cls.get_footer(target.rating)
#         thumbnail = cls.get_thumbnail(target, rating)

#         # convert rating ratio to positive percentage #
#         rating = rating * 100 if rating > 0.0 else rating * -100

#         description = strings.format_string(
#             description, target=target.display_name, rating=rating
#         )

#         footer

#         await cls.send_embed(
#             message,
#             title=title,
#             description=description,
#             thumbnail=thumbnail,
#             footer=footer,
#         )


class FishRate(RateBase):
    title = "❯ Fish Rate"
    description = "{target} is {rating}% Fish"

    fish = {
        "title": "❯ Fish!!",
        "thumbnail": "https://cdn.discordapp.com/emojis/1087018867055919164.webp?size=1024&quality=lossless",
    }

    user_overrides = {
        # Adriana
        1032686173849653425: fish,
        # adrihadry
        1110256621524885586: fish,
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)


class CuteRate(RateBase):
    title = "❯ Cute Rate"
    description = "{target} is 100% Cute"

    not_cute_descriptions = [
        "I'm sure {target} has a great...personality...",
        "{target}...?\n\nCute??..No.\n\nSorry, but no.",
        "{target}??\n\nLOL!!",
        "{target} is definitely *not* cute!",
    ]

    user_overrides = {
        # ruffiana
        474075064069783552: {"description": not_cute_descriptions}
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)


class BottomRate(RateBase):
    title = "❯ Bottom Rate"
    description = "{target} is {rating}% bottom"

    bottom = {
        "title": "❯ Bottom!!",
        "description": "❯ {target} is very bottom",
        "thumbnail": r"https://cdn.discordapp.com/emojis/1093690664119717939.webp?size=512&quality=lossless",
    }

    user_overrides = {
        # Butts
        641228870795657256: bottom,
        # Jessi
        117012698964819976: bottom,
        # Ryan
        843188175596945429: bottom,
        # Kirin
        140186220255903746: bottom,
        # ice
        819276102325239840: bottom,
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)


class StinkyRate(RateBase):
    title = "❯ Stinky Rate"
    description = "{target} is {rating}% stinky"
    thumbnail = r"https://cdn.discordapp.com/emojis/1318168707423408138.webp?size=96&quality=lossless"

    user_overrides = {
        # kirin
        819276102325239840: {
            "title": "❯ The Stinkiest",
            "description": "❯ Ice is the stinkiest.",
            "thumbnail": "https://cdn.discordapp.com/emojis/1318168707423408138.webp?size=96&quality=lossless",
        },
        843188175596945429: {
            "title": "❯ Super Stinky",
            "description": "❯ Ryan is super duper stinky.",
            "thumbnail": "https://cdn.discordapp.com/emojis/1318168707423408138.webp?size=96&quality=lossless",
        },
    }

    rating_overrides = {
        90: {"title": "❯ Super Stinky"},
        75: {"title": "❯ Very Stinky"},
        50: {"title": "❯ Stinky"},
        25: {"title": "❯ Kinda Stinky"},
        10: {"title": "❯ Not Stinky"},
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot
        super().__init__(parent, bot)


class RateAnything(RateBase):
    def __init__(self, parent, bot: Red, target: discord.Member, topic: str):
        super().__init__(parent, bot)

        self.topic = topic
        self.target = target

        self.rating = self.get_rating()

        self.topic_title = " ".join(word.capitalize() for word in self.topic.split())
        self.title = "❯ {topic} Rate".format(topic=self.topic_title)
        self.thumbnail = self.get_random_gif()
        self.description = "{target} is {rating}% {topic}".format(
            target=self.target.display_name, rating=self.rating, topic=self.topic
        )
        self.footer = r"The rate anything command is only available to supporters."

    def get_random_gif(self):
        # Search tenor for an appropriate thumbnail image
        search_term = self.topic.replace(" ", "-")
        gifs = web.get_tenor_gifs(search_term)
        gif_url = random.choice(gifs)

        return gif_url


class RateResponder(TextResponderBase):
    """Parent class that responds to any trigger containing 'rate'"""

    enabled: bool = True
    # \A: Asserts the position at the start of the string.
    # ([\w\s]+): Captures one or more word characters (letters, digits, and underscores) or spaces as the first word or words.
    # \s*: Matches zero or more whitespace characters.
    # rate: Matches the literal string "rate".
    pattern: str = r"\A([\w\s]+)\s*rate"
    ignore_case: bool = True

    rate_classes = {
        "gay": GayRate,
        "emma": EmmaRate,
        "dimbo": DimboRate,
        # "dom": DomRate,
        "fish": FishRate,
        "cute": CuteRate,
        "bottom": BottomRate,
        "stinky": StinkyRate,
    }

    def __init__(self, parent, bot: Red):
        self.parent = parent
        self.bot = bot

    async def respond(self, message: discord.Message, target: discord.Member = None):
        match = re.match(self.pattern, message.content, self.regex_flags)
        topic = match.group(1).strip()

        # this will ignore words that include 'rate' such as 'separate', 'celebrate', etc.
        if f"{topic.lower}rate" in IGNORE_WORDS:
            self.parent.logger.debug(
                f"Ignoring {f"{topic.lower}rate"} as it is in the ignore list."
            )
            return

        if topic.lower() in self.rate_classes:
            responder_class = self.rate_classes.get(topic.lower())
            responder = responder_class(self.parent, self.bot)
        else:
            responder_class = RateAnything
            responder = RateAnything(self.parent, self.bot, target=target, topic=topic)

        self.parent.logger.debug(
            f"Calling respond method from {responder_class.__name__}"
        )
        await responder.respond(message, target)
