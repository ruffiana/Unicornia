import platform
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def get_font_path():
    system = platform.system()
    if system == "Windows":
        return "calibri.ttf"  # Ensure this font is installed on Windows
    elif system == "Darwin":  # macOS
        return "Arial.ttf"  # A common font available on macOS
    else:  # Assume Linux or other
        return "LiberationSans-Regular.ttf"  # A similar font available on Linux


def get_text_size(text: str, font: ImageFont):
    dummy_image = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    dummy_draw = ImageDraw.Draw(dummy_image)
    text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    return (text_width, text_height)


def calculate_font_size(
    image_size: Tuple[int, int], text: str, base_font_size: int = 28
) -> int:
    width, height = image_size
    # Calculate the suggested font size based on image width and text length
    text_length_factor = len(text) / 2.0
    suggested_font_size = width // text_length_factor

    # Ensure the font size is not smaller than the base font size
    font_size = max(base_font_size, suggested_font_size)
    # Ensure the font size is not larger than half the width of the image
    font_size = min(font_size, width // 2)

    return font_size
