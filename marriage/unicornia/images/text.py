from collections import namedtuple
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .images import ImageUtil, Position

__all__ = ["TextDraw"]


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
