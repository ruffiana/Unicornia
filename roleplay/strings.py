"""String manipulation functions"""


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


if __name__ == "__main__":

    # testing format_string()
    test = "{target_member}, {invoker_member} wants to hug you."
    changed = format_string(
        test, invoker_member="Redbot", target_member="Ruffiana", target_owner="kirin"
    )
    print(changed)
