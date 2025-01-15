from pathlib import Path
import json
import logging
from typing import Optional, List, Dict, Any

from . import const


class Guilds:
    """
    A class to manage guild data for the Lovense bot.

    Attributes:
        GUILD_IDS (Optional[List[int]]): List of guild IDs from environment variable.
        DATA_FILEPATH (Path): Path to the data directory.
        GUILDS_FILEPATH (Path): Path to the guilds.json file.
        logger (logging.Logger): Logger for the class.
        parent (Optional[Any]): Parent instance.
        guilds (Dict[str, Any]): Dictionary containing guild data.
    """

    DATA_FILEPATH: Path = Path(__file__).parent / "data"
    GUILDS_FILEPATH: Path = DATA_FILEPATH / "guilds.json"

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the Guilds class.

        Args:
            parent (Optional[Any]): Parent instance.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.parent = parent

        self.guilds: Dict[str, Any] = self._load()

    @property
    def ids(self) -> List[int]:
        """
        Get the list of guild IDs.

        Returns:
            List[int]: List of guild IDs.
        """
        if not self.guilds:
            guild_ids = []
        else:
            guild_ids = [int(id_) for id_ in self.guilds.keys()]

        self.logger.debug(f"guild_ids: {guild_ids}")

        return guild_ids

    def user_ids(self, guild_id: int):
        guild = self.guilds.get(guild_id)
        if not guild:
            return []

        return list(guild.keys())

    def get(self, guild_id: int):
        guild = self.guilds.get(str(guild_id))
        return guild

    def add_user(self, guild_id: str, user_id: str, user: Any) -> None:
        """
        Add a user to a guild.

        Args:
            guild_id (str): The guild ID.
            uid (str): The user ID.
            user (Any): The user data.
        """
        self.logger.debug(
            f"add_user(guild_id: {guild_id}, user_id: {user_id}, user: {user}"
        )
        if guild_id not in self.guilds:
            self.guilds[guild_id] = {}

        self.guilds[guild_id][user_id] = user

        self._save()

    def _refresh(self) -> None:
        """Refresh the guild data by reloading it from the JSON file."""
        self.guilds = self._load()

    def _load(self) -> Dict[str, Any]:
        """
        Load guild data from the JSON file.

        Returns:
            Dict[str, Any]: Dictionary containing guild data.
        """
        self.logger.debug(f"_load()")
        if not self.GUILDS_FILEPATH.exists():
            self.logger.error(f"{self.GUILDS_FILEPATH} does not exist!")
            return {}

        guilds = {}
        with open(self.GUILDS_FILEPATH, "r") as f:
            try:
                guilds = json.load(f)
            except:
                self.logger.error(f"Error loading {self.GUILDS_FILEPATH}!")

        self.logger.debug(f"guilds data: {guilds}")
        return guilds

    def _save(self) -> None:
        """Save guild data to the JSON file."""
        with open(self.GUILDS_FILEPATH, "w") as f:
            json.dump(self.guilds, f, indent=4)


if __name__ == "__main__":
    guilds = Guilds()
    print(f"guild_ids: {guilds.ids}")
