import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from PIL import Image, ImageDraw, ImageFont
from collections import namedtuple


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


class ImageUtil:
    """Utility class for image manipulation using Pillow."""

    @staticmethod
    def load_image(base_image_path: str) -> Image.Image:
        """Loads the base image from the given path."""
        return Image.open(base_image_path).convert("RGBA")

    @staticmethod
    def get_image_dimensions(image_path: Path) -> Tuple[int, int]:
        """Get the dimensions of an image"""
        with Image.open(image_path) as img:
            # Returns (width, height)
            return img.size

    @staticmethod
    def rotate_image(image: Image, angle: float, resample=Image.BICUBIC):
        return image.rotate(angle, expand=1, resample=resample)

    @staticmethod
    def resize_image(image, scale=1.0):
        """Resize the given image uniformly by the specified scale."""
        width, height = image.size
        new_width = int(width * scale)
        new_height = int(height * scale)

        return image.resize((new_width, new_height), Image.LANCZOS)

    @classmethod
    def paste_centered(cls, base_image, overlay_image, position, rotation):
        rotated_image = cls.rotate_image(overlay_image, rotation)
        rotated_width, rotated_height = rotated_image.size
        # Calculate top-left corner for centering the rotated text image
        top_left_x = position[0] - rotated_width // 2
        top_left_y = position[1] - rotated_height // 2
        # Paste the rotated image onto the base image
        base_image.paste(rotated_image, (top_left_x, top_left_y), rotated_image)

    @staticmethod
    def draw_image_outline(base_image, outline_width=5, outline_color=(0, 0, 0, 255)):
        """Draw a solid color outline around the given image."""
        width, height = base_image.size
        outline_image = Image.new(
            "RGBA",
            (width + 2 * outline_width, height + 2 * outline_width),
            outline_color,
        )
        # Create a mask for the base image
        mask = Image.new("L", base_image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([0, 0, width, height], fill=255)
        # Paste the base image onto the outline image using the mask
        outline_image.paste(base_image, (outline_width, outline_width), mask)

        return outline_image


class TextDraw(ImageUtil):
    """Utility class for drawing text on images using Pillow."""

    FONTS_PATH = Path(__file__).parent / "fonts"
    TEXT_FONT = FONTS_PATH / "calibrib.ttf"
    EMOJI_FONT = FONTS_PATH / "NotoColorEmoji-Regular.ttf"

    def __init__(self, base_image_path: str):
        super().__init__()

        self.font_path = self.TEXT_FONT
        self.image = self.load_image(base_image_path)
        self.font = self.load_font()

    @staticmethod
    def get_contrast_color(
        color: str, dark_color: str = "black", light_color: str = "white"
    ) -> str:
        """Returns the color (dark or light) that provides the best contrast against the given color."""
        # Convert hex color to RGB
        color = color.lstrip("#")
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

        # Calculate the luminance of the color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        # Return dark color for light backgrounds and light color for dark backgrounds
        return dark_color if luminance > 0.5 else light_color

    @staticmethod
    def draw_text_outline(
        draw: ImageDraw.Draw,
        position: Position,
        text: str,
        font: ImageFont.FreeTypeFont,
        outline_color: str,
        outline_width: int,
    ) -> None:
        """Draws an outline around the text."""
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        (position.x + dx, position.y + dy),
                        text,
                        font=font,
                        fill=outline_color,
                    )

    @staticmethod
    def create_text_image(base_image: Image.Image) -> Image.Image:
        """Creates a transparent image for drawing text."""
        max_dimension = max(base_image.width, base_image.height)
        return Image.new("RGBA", (max_dimension, max_dimension), (255, 255, 255, 0))

    def load_font(self, font_size: int = 100) -> ImageFont.FreeTypeFont:
        """Loads the font from the given path or returns the default font."""
        return (
            ImageFont.truetype(self.font_path, font_size)
            if self.font_path
            else ImageFont.load_default()
        )

    @staticmethod
    def calculate_text_position(
        draw: ImageDraw.Draw,
        text: str,
        font: ImageFont.FreeTypeFont,
        image_center: Position,
    ) -> Position:
        """Calculates the position to center the text on the image."""
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = image_center.x - (text_width // 2)
        text_y = image_center.y - (text_height // 2)
        return Position(text_x, text_y)

    def draw_text(
        self,
        draw: ImageDraw.Draw,
        text_centered: Position,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: str = "black",
        outline: bool = False,
        outline_color: str = None,
        outline_width: Optional[int] = None,
        outline_scalar: float = 0.02,
    ) -> None:
        """Draws the text with optional outline."""
        if outline:
            if not outline_color:
                outline_color = self.get_contrast_color(color)
            outline_width = outline_width or max(4, int(font.size * outline_scalar))
            self.draw_text_outline(
                draw, text_centered, text, font, outline_color, outline_width
            )
        draw.text(text_centered, text, font=font, fill=color)

    @staticmethod
    def rotate_text_image(
        text_image: Image.Image, text_rotation: int = 0
    ) -> Image.Image:
        """Rotates the text image by the given angle."""
        if text_rotation != 0:
            return text_image.rotate(text_rotation, expand=True, resample=Image.BICUBIC)
        return text_image

    @staticmethod
    def calculate_offset(
        text_position: Position, rotated_size: tuple[int, int]
    ) -> Position:
        """Calculates the offset to position the rotated text image."""
        rotated_width, rotated_height = rotated_size
        offset_x = text_position.x - (rotated_width // 2)
        offset_y = text_position.y - (rotated_height // 2)
        return Position(offset_x, offset_y)

    def calculate_font_size(self, text: str) -> int:
        """Calculates the font size to fit the text within the image width."""
        draw = ImageDraw.Draw(self.image)
        initial_font_size = 10
        font = ImageFont.truetype(self.font_path, initial_font_size)

        # Calculate the bounding box of the text with the initial font size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        # Calculate the margin and the available width for the text
        margin = max(2, self.image.width // 10)
        available_width = self.image.width - (2 * margin)

        # Calculate the scale factor to fit the text within the available width
        scale_factor = available_width / text_width

        # Return the scaled font size
        return int(initial_font_size * scale_factor)

    def draw_header_text(
        self,
        text: str,
        color: str = "black",
        outline: bool = False,
        outline_color: str = "white",
        outline_width: Optional[int] = None,
        outline_scalar: float = 0.0125,
    ) -> Image.Image:
        """Draws text on the image with automatically calculated font size."""
        # Calculate the appropriate font size
        font_size = self.calculate_font_size(text)

        # Load the font with the calculated size
        font = self.load_font(font_size)

        # Create a drawing context
        draw = ImageDraw.Draw(self.image)

        # Calculate the bounding box of the text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate the margin and centered position
        margin = max(2, self.image.height // 20)  # Adjusted margin to place text higher
        image_center = Position(self.image.width // 2, self.image.height // 2)
        centered_position = Position(image_center.x, margin + (text_height // 2))

        # Draw the text on the image
        return self.draw_text_on_image(
            text=text,
            position=centered_position,
            font_size=font_size,
            color=color,
            outline=outline,
            outline_color=outline_color,
            outline_width=outline_width,
            outline_scalar=outline_scalar,
        )

    def draw_text_on_image(
        self,
        text: str,
        position: Position = Position(0, 0),
        rotation: int = 0,
        font_size: int = 100,
        color: str = "black",
        outline: bool = False,
        outline_color: str = "white",
        outline_width: Optional[int] = None,
        outline_scalar: float = 0.02,
    ) -> Image.Image:
        """Draws text on the image with the specified parameters."""
        image_center = Position(self.image.width // 2, self.image.height // 2)
        text_image = self.create_text_image(self.image)
        font = self.load_font(font_size)
        draw = ImageDraw.Draw(text_image)
        text_centered = self.calculate_text_position(draw, text, font, image_center)
        self.draw_text(
            draw,
            text_centered,
            text,
            font,
            color,
            outline,
            outline_color,
            outline_width,
            outline_scalar,
        )
        text_image = self.rotate_text_image(text_image, rotation)
        offset = self.calculate_offset(position, text_image.size)
        self.image.paste(text_image, offset, text_image)
        return self.image


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
        self.logger.setLevel(logging.DEBUG)

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

        proc = random.randrange(1, 100)
        if proc <= 5:
            return 0
        elif proc >= 95:
            return 10
        else:
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

        # get a random score for each position/rotation and draw them on the image
        for position, rotation in zip(image_data.positions, image_data.rotations):
            # Draw each score on the image at the specified positions with the given rotation
            score = self.get_random_score()
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
