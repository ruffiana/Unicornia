import logging
import random
import yaml
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

from .flags import flag_emojis


@dataclass
class ImageData:
    base_image_path: Path
    positions: List[Tuple[int, int]]
    size: int
    color: str
    rotations: List[int]


class JudgesScoreboardGenerator:
    # Class constants for the output directory and config file path
    OUTPUT_DIR = Path(__file__).resolve().parent / "output_images"
    PATH_IMAGES = Path(__file__).resolve().parent / "images"
    IMAGES_DATA = PATH_IMAGES / "images.yaml"
    TEXT_FONT = "calibri.ttf"
    EMOJI_FONT = Path(__file__).parent / "fonts" / "NotoColorEmoji-Regular.ttf"

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)

        self.images = self.load_images_data()
        # Ensure the output directory exists
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # check fonts
        if not self.EMOJI_FONT.is_file():
            self.logger.error(f"{self.EMOJI_FONT} is not a valid font")

    @classmethod
    def load_images_data(cls):
        with open(cls.IMAGES_DATA, "r") as file:
            raw_config = yaml.safe_load(file)
        config = {}
        for image_name, details in raw_config.items():
            base_image_path = cls.PATH_IMAGES / image_name
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

    @staticmethod
    def get_image_dimensions(image_path: Path) -> Tuple[int, int]:
        with Image.open(image_path) as img:
            return img.size  # Returns (width, height)

    def calculate_font_size(
        self, image_width: int, text_length: int, base_font_size: int = 28
    ) -> int:
        # Basic formula to calculate font size
        self.logger.debug(
            f"image_width: {image_width}, text_length: {text_length}, base_font_size: {base_font_size}"
        )
        font_size = max(base_font_size, image_width // (text_length / 1.5))
        self.logger.debug(f"font_size: {font_size}")
        return font_size

    @staticmethod
    def generate_weighted_float_score(alpha: int = 2, beta: int = 1):
        score = random.betavariate(alpha, beta)
        weighted_score = 1 + (score * 9)
        rounded_score = round(weighted_score, 1)

        if rounded_score == 10.0:
            return 10
        else:
            return rounded_score

    @classmethod
    def calculate_rotated_size(cls, width, height, angle):
        radians = math.radians(angle)
        new_width = abs(width * math.cos(radians)) + abs(height * math.sin(radians))
        new_height = abs(width * math.sin(radians)) + abs(height * math.cos(radians))
        return int(new_width), int(new_height)

    @classmethod
    def create_text_image(cls, text, font_size, color, rotation):
        font = ImageFont.truetype(cls.TEXT_FONT, font_size)
        dummy_image = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
        dummy_draw = ImageDraw.Draw(dummy_image)
        text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        new_width, new_height = cls.calculate_rotated_size(
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
    def rotate_image(cls, image, angle):
        return image.rotate(angle, expand=1, resample=Image.BICUBIC)

    @classmethod
    def paste_centered(cls, base_image, text_image, position, rotation):
        rotated_image = cls.rotate_image(text_image, rotation)
        rotated_width, rotated_height = rotated_image.size
        # Calculate top-left corner for centering the rotated text image
        top_left_x = position[0] - rotated_width // 2
        top_left_y = position[1] - rotated_height // 2
        # Paste the rotated image onto the base image
        base_image.paste(rotated_image, (top_left_x, top_left_y), rotated_image)

    def draw_score(self, base_image, position, score, font_size, rotation, color):
        text = str(score)
        text_image, text_width, text_height = self.create_text_image(
            text, font_size, color, rotation
        )
        self.paste_centered(base_image, text_image, position, rotation)

    def draw_text(
        self, draw, text, image_width, color="#FFFFFF", outline_color="#000000"
    ):
        # Calculate font size based on image width and text length
        font_size = self.calculate_font_size(image_width, len(text))
        text_font = ImageFont.truetype(self.TEXT_FONT, font_size)
        text_width, text_height = self.get_text_size(text, text_font)
        text_position = (
            (image_width - text_width) // 2,
            10,
        )  # Top-centered with a small vertical margin

        outline_width = int(font_size // 25)

        # Draw outline
        for offset in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset != 0 or offset_y != 0:
                    draw.text(
                        (text_position[0] + offset, text_position[1] + offset_y),
                        text,
                        font=text_font,
                        fill=outline_color,
                    )

        # Draw text
        draw.text(text_position, text, font=text_font, fill=color)

    def create(self, text: Optional[str] = None):
        image_name = random.choice(list(self.images.keys()))

        image_data = self.images[image_name]
        base_image_path = image_data.base_image_path

        # Get the dimensions of the base image
        width, height = self.get_image_dimensions(base_image_path)
        print(f"Base image dimensions: {width}x{height}")

        # Open the base image
        base_image = Image.open(base_image_path)
        draw = ImageDraw.Draw(base_image)

        # Draw the text at the top of the image if provided
        if text:
            self.draw_text(draw, text, width, outline_color=image_data.color)

        # Generate random scores based on the number of positions
        scores = [
            self.generate_weighted_float_score()
            for _ in range(len(image_data.positions))
        ]

        # Draw each score on the image at the specified positions with the given rotation
        for position, score, rotation in zip(
            image_data.positions, scores, image_data.rotations
        ):
            self.draw_score(
                base_image, position, score, image_data.size, rotation, image_data.color
            )

        # Create the output path dynamically
        output_image_path = self.OUTPUT_DIR / f"{image_name}_output.jpg"
        base_image.save(output_image_path)
        return output_image_path

    def get_text_size(self, text: str, font: ImageFont):
        dummy_image = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
        dummy_draw = ImageDraw.Draw(dummy_image)
        text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return text_width, text_height

    def draw_flag(self, draw, flag, position, font_size):
        try:
            flag_font = ImageFont.truetype(self.TEXT_FONT, font_size)
            text_width, text_height = self.get_text_size(flag, flag_font)
            flag_position = (
                position[0] - text_width // 2,
                position[1] + font_size + 50 - text_height // 2,
            )

            # Draw some debug text to verify font loading
            draw.text((10, 10), "Debug Text", font=flag_font, fill="black")
            draw.text(flag_position, flag, font=flag_font, fill="black")

            print(
                f"Flag {flag} drawn at position {flag_position} with size ({text_width}, {text_height})"
            )
        except Exception as e:
            print(f"Error drawing flag: {e}")


if __name__ == "__main__":
    # Create an instance of the JudgesScoreboardGenerator class
    scoreboard_generator = JudgesScoreboardGenerator()

    # Generate judges scoreboard images for all images
    for image_name in scoreboard_generator.images:
        result = scoreboard_generator.create(image_name)
        print(result)
