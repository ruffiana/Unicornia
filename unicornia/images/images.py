from collections import namedtuple
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw


__all__ = ["Position", "ImageUtil"]

# this uses a namedtuple to represent an x, y position. We can't use a
# dataclass because Pillow will try to access it using index notation
Position = namedtuple("Position", ["x", "y"])


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
