import logging

LOG_LEVEL = logging.INFO

UNICORNIA_BOT_COLOR = 5778572
PRIDE_EMOJI = "🏳️‍🌈"
PRIDE_HEART = "https://cdn.discordapp.com/emojis/1088555199146242248.webp?size=128&quality=lossless"

# commonly used user IDs
KIRIN_ID = 140186220255903746
RUFFIANA_ID = 474075064069783552
JUNNY_ID = 89582933735665664
SIENNA_ID = 352087314282971136
RADON_ID = 144523162044858368

# these are the user IDs of the people who are always responded to
# they can be extended in the individual responder classes
ALWAYS_RESPOND = [RUFFIANA_ID]

# these are the user IDs of the people who are never responded to
# they can be extended in the individual responder classes
NEVER_RESPOND = [JUNNY_ID, 352087314282971136]

# per-guild server permissions
# this is pretty basic right now, but could be used to limit specific
# responders to specific channels or servers, override always/never
# respond lists, etc
SERVER_PERMISSIONS = {
    760220886460137513: {
        "name": "Ruffiana's Playground",
        "allowed_channels": {1318299981668552735: "redbot"},
    },
    684360255798509578: {
        "name": "Unicornia",
        "allowed_channels": {
            686096388018405408: "bot-commands",
            1081656723904921651: "bot-dungeon",
            778700678851723295: "comfy-chat",
            686091486327996459: "horny-jail",
            686092688059400454: "bot-spam",
        },
    },
}
