from digiprod_gen.frontend.js import get_screen_width
from digiprod_gen.frontend.session import get_session_id


def is_mobile() -> bool:
    try:
        width: int = get_screen_width(get_session_id())
    except TypeError:
        # Thrown if screen width is not know yet
        return False
    return width < 600


