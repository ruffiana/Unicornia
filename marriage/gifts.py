import logging

from redbot.core.bot import Red

from dataclasses import dataclass
import yaml
from pathlib import Path


@dataclass
class Gift:
    contentment: int = 1
    description: str = ":gift: {author} has gifted one {item} to {target}"


class Gifts:
    DATA_PATH = Path(__file__).parent / "gifts.yml"

    def __init__(self, bot: Red = None, parent=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.bot = bot
        self.parent = parent

        self.gifts_data = self.load()

    def load(self):
        if not self.DATA_PATH.exists():
            self.logger.warning(f"{self.DATA_PATH} does not exist.")
            return {}

        with open(self.DATA_PATH, "r") as file:
            try:
                gifts = yaml.safe_load(file)
                return {name: Gift(**data) for name, data in gifts.items()}
            except yaml.YAMLError as e:
                self.logger.error(f"Error loading data from {self.DATA_PATH}: {e}")
                return {}

    def get(self, name) -> dict:
        return self.gifts_data.get(name, None)

    def as_list(self) -> str:
        return list(self.gifts_data.keys())

    def show(self, gift_name: str) -> dict:
        gift = self.gifts_data.get(gift_name.lower())
        if not gift:
            return f'"{gift_name}" is not a valid gift.'

        display_text = f"= {gift_name.capitalize()} =\nContentment: {gift.contentment}"
        return display_text


# this is just here for testing purposes
if __name__ == "__main__":
    import asyncio

    async def main():
        gifts = Gifts()
        print(gifts.gifts_data)
        print(gifts.get("flower"))
        print(gifts.as_list())

    asyncio.run(main())
