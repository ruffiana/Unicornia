from pathlib import Path

# server IDs
RUFFIANAS_PLAYGROUND_ID = 760220886460137513
UNICORNIA_ID = 684360255798509578

# channel IDs per server
CONTEST_CHANNEL_IDS = {
    RUFFIANAS_PLAYGROUND_ID: 1318299981668552735,
    UNICORNIA_ID: 1081656723904921651,
}

COLOR = 3553598
UNICORNIA_BOT_COLOR = 5778572

FOOTER_TEXT = "Unicornia | Cutie of the Month Contest {contest_number}"
FOOTER_ICON_URL = r"https://i.imgur.com/jy8AWEI.png"

DATA_PATH = Path(__file__).parent / "data"

CONTEST_TITLE = "Unicornia Cutie of the Month Contest"
CONTEST_DESCRIPTION = DATA_PATH / "contest.txt"

TERMS_TITLE = "Entry Terms"
TERMS_DESCRIPTION = DATA_PATH / "terms.txt"

PRIZES_TITLE = "Prizes"
PRIZES_DESCRIPTION = DATA_PATH / "contest.txt"

VOTES_TITLE = "How to cast votes"
VOTES_DESCRIPTION = DATA_PATH / "votes.txt"
