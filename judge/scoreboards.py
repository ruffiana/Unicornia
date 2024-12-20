import itertools
import logging
import math
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from . import fonts

# Class constants for the output directory and config file path
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output_images"
IMAGES_DIR = BASE_DIR / "images"


@dataclass
class ImageData:
    base_image_path: Path
    positions: List[Tuple[int, int]]
    size: int
    color: str
    rotations: List[int]


class ImageUtil:
    FONTS_PATH = Path(__file__).parent / "fonts"
    TEXT_FONT = FONTS_PATH / "calibrib.ttf"
    EMOJI_FONT = FONTS_PATH / "NotoColorEmoji-Regular.ttf"

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
    def calculate_rotated_size(cls, width, height, angle):
        radians = math.radians(angle)
        new_width = abs(width * math.cos(radians)) + abs(height * math.sin(radians))
        new_height = abs(width * math.sin(radians)) + abs(height * math.cos(radians))
        return int(new_width), int(new_height)

    def create_text_image(self, text, font_size, color, rotation):
        font = ImageFont.truetype(self.TEXT_FONT, font_size)
        dummy_image = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
        dummy_draw = ImageDraw.Draw(dummy_image)
        text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        new_width, new_height = self.calculate_rotated_size(
            text_width, text_height, rotation
        )

        # Making the image size twice as large to avoid clipping
        new_width *= 2
        new_height *= 2

        text_image = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_image)
        # Draw text in the center of the larger image
        draw_x = (new_width - text_width) // 2
        draw_y = (new_height - text_height) // 2
        text_draw.text((draw_x, draw_y), text, font=font, fill=color)
        return text_image, new_width, new_height

    @classmethod
    def paste_centered(cls, base_image, overlay_image, position, rotation):
        rotated_image = cls.rotate_image(overlay_image, rotation)
        rotated_width, rotated_height = rotated_image.size
        # Calculate top-left corner for centering the rotated text image
        top_left_x = position[0] - rotated_width // 2
        top_left_y = position[1] - rotated_height // 2
        # Paste the rotated image onto the base image
        base_image.paste(rotated_image, (top_left_x, top_left_y), rotated_image)

    def draw_text_outline(
        self, draw, x, y, word, font, font_size, outline_color="#000000"
    ):
        outline_width = max(min(int(font_size // 50), 8), 4)
        offsets = itertools.product(range(-outline_width, outline_width + 1), repeat=2)
        for offset_x, offset_y in offsets:
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y),
                    word,
                    font=font,
                    fill=outline_color,
                )

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

    def draw_text(
        self,
        draw,
        text,
        image_size: Tuple[(int, int)],
        color="#FFFFFF",
        outline_color="#000000",
    ):
        image_height, image_width = image_size

        # Calculate font size based on image width and text length
        font_size = fonts.calculate_font_size(image_size, text)
        text_font = ImageFont.truetype(self.TEXT_FONT, font_size)
        text_width, text_height = fonts.get_text_size(text, text_font)
        text_position = (
            (image_width - text_width) // 2,
            10,
        )  # Top-centered with a small vertical margin

        x, y = text_position
        words = re.split(r"(\W)", text)  # Split text into words and keep punctuation

        for word in words:
            text_bbox = draw.textbbox((0, 0), word, font=text_font)
            word_width = text_bbox[2] - text_bbox[0]
            word_height = text_bbox[3] - text_bbox[1]

            # Draw outline
            self.draw_text_outline(
                draw, x, y, word, text_font, font_size, outline_color
            )

            # Draw text
            draw.text((x, y), word, font=text_font, fill=color)

            x += word_width  # Move x position for the next word


class FlagsUtil(ImageUtil):
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


class ScoreUtil(ImageUtil):
    @staticmethod
    def get_random_score(alpha: int = 12, beta: int = 1):
        score = random.betavariate(alpha, beta)
        weighted_score = 1 + (score * 9)
        rounded_score = round(weighted_score, 1)

        if rounded_score == 10.0:
            return 10
        else:
            return rounded_score

    def draw_score(self, base_image, position, score, font_size, rotation, color):
        text = str(score)
        text_image, text_width, text_height = self.create_text_image(
            text, font_size, color, rotation
        )
        self.paste_centered(base_image, text_image, position, rotation)


class Generator(ImageUtil):
    IMAGES_DATA = IMAGES_DIR / "images.yaml"

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)

        self.images_data = self.load_images_data()

        self.flags_util = FlagsUtil()
        self.score_util = ScoreUtil()

        # Ensure the output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # check fonts
        if not self.EMOJI_FONT.is_file():
            self.logger.error(f"{self.EMOJI_FONT} is not a valid font")

    @classmethod
    def load_images_data(cls):
        with open(cls.IMAGES_DATA, "r") as file:
            raw_config = yaml.safe_load(file)
        config = {}
        for image_name, details in raw_config.items():
            base_image_path = IMAGES_DIR / image_name
            positions = details.get("positions", [])
            size = details.get("size", 12)  # Default size 12
            color = details.get("color", "#000000")  # Default color black
            # Default rotation 0. Need to have same number of rotations as positions
            rotations = details.get("rotations", [0] * len(positions))

            config[image_name] = ImageData(
                base_image_path=base_image_path,
                positions=positions,
                size=size,
                color=color,
                rotations=rotations,
            )
        return config

    def create(self, text: Optional[str] = None, text_color=None):
        image_name = random.choice(list(self.images_data.keys()))

        image_data = self.images_data[image_name]
        base_image_path = image_data.base_image_path

        # Get the dimensions of the base image
        image_size = self.get_image_dimensions(base_image_path)

        # Open the base image
        base_image = Image.open(base_image_path)
        draw = ImageDraw.Draw(base_image)

        # Draw the text at the top of the image if provided
        if text:
            self.draw_text(
                draw,
                text,
                image_size,
                color=text_color if text_color else None,
                outline_color=image_data.color,
            )

        # Generate random scores based on the number of positions
        proc = random.randrange(1, 100)
        if proc <= 5:
            scores = [0] * len(image_data.positions)
        elif proc >= 95:
            scores = [10] * len(image_data.positions)
        else:
            scores = [
                self.score_util.get_random_score()
                for _ in range(len(image_data.positions))
            ]

        # Draw each score on the image at the specified positions with the given rotation
        for position, score, rotation in zip(
            image_data.positions, scores, image_data.rotations
        ):
            self.score_util.draw_score(
                base_image, position, score, image_data.size, rotation, image_data.color
            )
            nation, flag_image_path = self.flags_util.get_random_flag()
            flag_x, flag_y = position
            flag_y = base_image.size[1] - 100
            self.flags_util.overlay_flag(
                base_image, flag_image_path, (flag_x, flag_y), scale=1.0
            )

        # Create the output path dynamically
        output_image_path = OUTPUT_DIR / f"judges_scores.jpg"
        base_image.save(output_image_path)
        return output_image_path
