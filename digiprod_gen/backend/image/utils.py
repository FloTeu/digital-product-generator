from typing import Tuple

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    # Remove the "#" character if present
    hex_color = hex_color.lstrip('#')

    # Convert the hex color to an RGB tuple
    rgb = tuple(int(hex_color[i: i +2], 16) for i in (0, 2, 4))

    return rgb

def hex_to_rgba(hex_color: str, alpha_channel: int=255) -> Tuple[int, int, int]:
    """Adds an alpha channel to rgb output"""
    return hex_to_rgb(hex_color) + (alpha_channel,)