from digiprod_gen.frontend.js import get_screen_width

def is_mobile() -> bool:
    width: int | None = get_screen_width()
    if width is None:
        return False
    return width < 600