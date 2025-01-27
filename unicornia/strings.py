"""String manipulation functions"""

import re


def replace_pronouns(text):
    REPLACEMENTS = {
        "i": "you",
        "me": "you",
        "my": "your",
        "mine": "yours",
        "we": "you all",
        "us": "you all",
        "our": "your",
        "ours": "yours",
    }

    words = text.split()
    replaced_words = []
    for word in words:
        stripped_word = word.strip(",.!?;:")
        if stripped_word in REPLACEMENTS:
            replaced_words.append(REPLACEMENTS[stripped_word])
        else:
            replaced_words.append(word)

    return " ".join(replaced_words)


def get_indefinite_article(word: str) -> str:
    """
    Determine the correct indefinite article ("a" or "an") for a given word.

    Args:
        word (str): The word to determine the article for.

    Returns:
        str: "a" or "an" based on the initial sound of the word.
    """
    # Define vowels and special cases
    vowels = "aeiou"
    special_cases = {"hour": "an", "honest": "an", "heir": "an", "honor": "an"}

    # Convert word to lowercase for consistency
    word = word.lower()

    # Check for special cases
    if word in special_cases:
        return special_cases[word]

    # Use "an" if the word starts with a vowel sound
    if word[0] in vowels:
        return "an"

    # Default to "a"
    return "a"


def pluralize(noun: str) -> str:
    """
    Convert a singular noun to its plural form.

    Args:
        noun (str): The singular noun to pluralize.

    Returns:
        str: The plural form of the noun.
    """
    # Common irregular nouns
    irregular_nouns = {
        "child": "children",
        "man": "men",
        "woman": "women",
        "tooth": "teeth",
        "foot": "feet",
        "mouse": "mice",
        "person": "people",
        "goose": "geese",
    }

    # Check for irregular nouns
    if noun in irregular_nouns:
        return irregular_nouns[noun]

    # Words that end in 'y' and preceded by a consonant
    if noun.endswith("y") and noun[-2] not in "aeiou":
        return noun[:-1] + "ies"

    # Words that end in 's', 'sh', 'ch', 'x', or 'z'
    if noun.endswith(("s", "sh", "ch", "x", "z")):
        return noun + "es"

    # Words that end in 'f' or 'fe'
    if noun.endswith("f"):
        return noun[:-1] + "ves"
    if noun.endswith("fe"):
        return noun[:-2] + "ves"

    # Default rule: add 's'
    return noun + "s"


def format_string(template: str, **kwargs) -> str:
    """Format the given template string with provided keyword arguments
    only if the placeholders are present in the string.

    Args:
        template (str): The template string containing placeholders.
        kwargs: Keyword arguments with replacement values.

    Returns:
        str: The formatted string.
    """
    for key, value in kwargs.items():
        placeholder = f"{{{key}}}"

        if placeholder in template:
            template = template.replace(placeholder, str(value))

    return template


def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def dict_to_string(data: dict) -> str:
    """Convert a dictionary to a string representation.

    Args:
        data (dict): The dictionary to convert to a string.

    Returns:
        str: The string representation of the dictionary.
    """
    return "\n".join(f"{key}: {value}" for key, value in data.items())


def add_ordinal_suffix(number: int) -> str:
    """
    Add the appropriate ordinal suffix to an integer.

    Args:
        number (int): The integer to add the suffix to.

    Returns:
        str: The integer with its ordinal suffix.
    """
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

    return f"{number}{suffix}"
