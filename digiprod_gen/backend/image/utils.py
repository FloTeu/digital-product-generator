from typing import Tuple
from PIL import Image

def is_jpeg(image):
    """
    Check if a Pillow Image object is a JPEG.

    :param image: Pillow Image object
    :return: True if the image is JPEG, False otherwise (including if it's a PNG)
    """
    return image.format == 'JPEG'

def is_png(image):
    """
    Check if a Pillow Image object is a PNG.

    :param image: Pillow Image object
    :return: True if the image is PNG, False otherwise
    """
    return image.format == 'PNG'

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    # Remove the "#" character if present
    hex_color = hex_color.lstrip('#')

    # Convert the hex color to an RGB tuple
    rgb = tuple(int(hex_color[i: i +2], 16) for i in (0, 2, 4))

    return rgb

def hex_to_rgba(hex_color: str, alpha_channel: int=255) -> Tuple[int, int, int]:
    """Adds an alpha channel to rgb output"""
    return hex_to_rgb(hex_color) + (alpha_channel,)