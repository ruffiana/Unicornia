import logging

from redbot.core.bot import Red

from dataclasses import dataclass
import yaml
from pathlib import Path


@dataclass
class Action:
    contentment: int = 5
    require_consent: bool = False
    consent_description: str = ""
    description: str = ""
    emoji: str = ""


class Actions:
    DATA_PATH = Path(__file__).parent / "actions.yml"

    def __init__(self, bot: Red = None, parent=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.bot = bot
        self.parent = parent

        self.actions_data = self.load()

    def load(self) -> dict:
        if not self.DATA_PATH.exists():
            self.logger.warning(f"{self.DATA_PATH} does not exist.")
            return {}

        with open(self.DATA_PATH, "r") as file:
            try:
                actions = yaml.safe_load(file)
                return {name: Action(**data) for name, data in actions.items()}
            except yaml.YAMLError as e:
                self.logger.error(f"Error loading data from {self.DATA_PATH}: {e}")
                return {}

    def get(self, name) -> dict:
        return self.actions_data.get(name, None)

    def show(self, action_name: str) -> dict:
        action = self.actions_data.get(action_name.lower())
        if not action:
            return f'"{action_name}" is not a valid action.'

        display_text = f"""= {action_name.capitalize()} =\nContentment: {action.contentment}\nRequire Consent: {action.require_consent}"""
        return display_text

    def as_list(self) -> str:
        return list(self.actions_data.keys())


# this is just here for testing purposes
if __name__ == "__main__":
    actions = Actions()
    print(actions.actions_data)
    print(actions.get("date"))
    print(actions.as_list())
    print(actions.show("date"))
