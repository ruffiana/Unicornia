import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from PIL import Image
from collections import namedtuple

from unicornia.images import ImageUtil, Position
from unicornia.images import TextDraw

# Class constants for the output directory and config file path
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output_images"
IMAGES_DIR = BASE_DIR / "images"


# this uses a namedtuple to represent an x, y position. We can't use a
# dataclass because Pillow will try to access it using index notation
Position = namedtuple("Position", ["x", "y"])


@dataclass
class ScoreboardBaseImage:
    """
    A class to represent a scoreboard image.

    Attributes:
    ----------
    image_filepath : Path
        The file path to the image.
    positions : List[Tuple[int, int]]
        A list of tuples representing the positions on the scoreboard.
    size : int
        The size of the scoreboard.
    color : str
        The color of the scoreboard.
    rotations : List[int]
        A list of integers representing the rotations of the scoreboard.
    """

    image_filepath: Path
    positions: List[Tuple[int, int]]
    size: int
    color: str
    rotations: List[int]

    def __post_init__(self):
        self.positions = [Position(x, y) for x, y in self.positions]


class FlagDraw(ImageUtil):
    """Utility class for drawing flag images on images using Pillow."""

    FLAG_PATH = IMAGES_DIR / "flag"
    OUTPUT_PATH = BASE_DIR / "output_images" / "flag_test.png"

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)
        self.flags = self.get_all_flags()

    @classmethod
    def get_all_flags(cls):
        """Get a list of all flag images from the flag path."""
        return [f for f in cls.FLAG_PATH.iterdir() if f.is_file()]

    def get_random_flag(self):
        """Get a random flag image from the flag path and extract the nation name."""
        random_flag = random.choice(self.flags)
        match = re.search(r"Flag_of_(.*)\.svg\.png", random_flag.name)
        nation_name = match.group(1).replace("_", " ") if match else "Unknown"
        return nation_name, random_flag

    @classmethod
    def overlay_flag(
        cls,
        base_image,
        flag_image_path,
        position=(0, 0),
        scale=1.0,
    ):
        # Open the flag image
        flag_image = Image.open(flag_image_path).convert("RGBA")

        # Resize the flag image to fit the base image while keeping the aspect ratio
        flag_image = cls.resize_image(flag_image, scale)

        flag_image = cls.draw_image_outline(flag_image)

        # Paste the flag image onto the base image at the specified position
        cls.paste_centered(base_image, flag_image, position, rotation=0)

        return base_image


class ScoreboardMaker:
    """A class to generate scoreboard images with random scores and flags."""

    IMAGES_DATA = IMAGES_DIR / "images.yaml"

    def __init__(self, logger=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        self.images_data = self.load_scoreboard_images_data()

        self.flags_util = FlagDraw()

        # Ensure the output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_random_score(alpha: int = 12, beta: int = 1):
        """
        Generate a random score between 0 and 10.

        The function generates a random score between 0 and 10. The score is determined by a random
        process where:
        - There is a 5% chance of returning a score of 0.
        - There is a 5% chance of returning a score of 10.
        - Otherwise, the score is generated using a beta distribution with the given alpha and beta
          parameters, scaled to a range of 1 to 10, and rounded to one decimal place.

        Parameters:
            alpha (int): The alpha parameter for the beta distribution. Default is 12.
            beta (int): The beta parameter for the beta distribution. Default is 1.
        Returns:
            float: A random score between 0 and 10, inclusive.
        """
        score = random.betavariate(alpha, beta)
        weighted_score = 1 + (score * 9)
        rounded_score = round(weighted_score, 1)

        if rounded_score == 10.0:
            return 10
        else:
            return rounded_score

    @classmethod
    def load_scoreboard_images_data(cls):
        """Load the scoreboard images data from the config file."""
        with open(cls.IMAGES_DATA, "r") as file:
            try:
                raw_config = yaml.safe_load(file)
            except yaml.YAMLError as e:
                raise ValueError(f"Error loading images data: {e}")
                return {}

        config = {}
        for image_name, details in raw_config.items():
            image_filepath = IMAGES_DIR / image_name
            positions = details.get("positions", ())
            size = details.get("size", 12)  # Default size 12
            color = details.get("color", "#000000")  # Default color black
            # Default rotation 0. Need to have same number of rotations as positions
            rotations = details.get("rotations", [0] * len(positions))

            config[image_name] = ScoreboardBaseImage(
                image_filepath=image_filepath,
                positions=positions,
                size=size,
                color=color,
                rotations=rotations,
            )

        return config

    def create_scoreboard(self, text: Optional[str] = None, text_color=None):
        """
        Creates a scoreboard image with random scores and optional header text.

        Args:
            text (Optional[str]): The header text to be drawn on the image. Defaults to None.
            text_color: The color of the header text. If not provided, the default color from image data will be used.

        Returns:
            str: The file path of the saved scoreboard image.
        """
        image_name = random.choice(list(self.images_data.keys()))

        image_data = self.images_data[image_name]
        base_image_path = image_data.image_filepath

        # Open the base image
        text_draw = TextDraw(base_image_path)

        # Draw the header text on the image if supplied
        if text:
            text_draw.draw_header_text(
                text, color=text_color if text_color else image_data.color, outline=True
            )

        # get a random score for each position
        proc = random.randrange(1, 100)
        num_needed = len(image_data.positions)
        # 5% chance for all 10 or all 0
        if proc <= 5:
            scores = [0] * num_needed
        elif proc >= 95:
            scores = [10] * num_needed
        else:
            scores = [self.get_random_score() for _ in range(num_needed)]

        # Draw each score on the image at the specified positions with the given rotation
        for position, rotation, score in zip(
            image_data.positions, image_data.rotations, scores
        ):
            text_draw.draw_text_on_image(
                str(score),
                position=position,
                rotation=rotation,
                font_size=image_data.size,
                color=image_data.color,
                outline=False,
            )

            # draw a random flag aligned vertically with each scoreboard
            nation, flag_image_path = self.flags_util.get_random_flag()
            flag_x, flag_y = position
            flag_y = (
                text_draw.image.size[1] - 100
            )  # align the flag 100 pixels from the bottom of the image
            self.flags_util.overlay_flag(
                text_draw.image, flag_image_path, (flag_x, flag_y), scale=1.0
            )

        final_image = text_draw.image

        # Create the output path dynamically
        output_image_path = OUTPUT_DIR / f"judges_scores.png"
        final_image.save(output_image_path)
        # final_image.show()
        return output_image_path
