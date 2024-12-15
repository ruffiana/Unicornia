USER_SETTINGS = {
    "owners": {
        "aliases": ["owner"],
        "default": [],
        "label": "Owner",
        "description": "Always consent to any action from your owner. Owners are also asked for consent instead of you.",
        "emoji": "👑",
        "permission": {
            "required": True,
            "permission_ask": "{target}, {author} would like you to be their Owner. Do you agree?",
            "permission_accept": "{target} is now your owner, {author}.",
            "permission_deny": "Sorry, {author}. {target} declined to become your Owner.",
        },
    },
    "allowed": {
        "aliases": ["allow", "approved", "approve"],
        "default": [],
        "label": "Allowed User",
        "description": "Always consent to any action from members in your allowed list.",
        "emoji": "✅",
    },
    "blocked": {
        "aliases": ["block"],
        "default": [],
        "label": "Blocked User",
        "description": "Ignore any roleplay command from members in your blocked list.",
        "emoji": "🚫",
    },
    "selective": {
        "default": False,
        "label": "Selective User",
        "description": "Will always reject roleplay commands from any user not in their allowed list.",
        "emoji": "🛡️",
    },
    "public": {
        "default": False,
        "label": "Public Use Slut",
        "description": "Always consent to any action from any member except those in your blocked list.",
        "emoji": "🆓",
    },
    # example of extending settings
    # "keyholders" : {
    #     "default" : [],
    #     "label": "Keyholder(s)",
    #     "description": "Keyholder is responsible for managing your chastity.",
    #     "emoji": "🗝️"
    #     },
    # "chastity": {
    #     "default : False",
    #     "label": "Chastity",
    #     "description": "Properties for chastity.",
    #     "emoji": "🔒🔓"
    #     },
}
