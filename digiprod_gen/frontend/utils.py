from streamlit.runtime.scriptrunner import add_script_run_ctx
from digiprod_gen.frontend.js import get_screen_width


def is_mobile() -> bool:
    try:
        width: int = get_screen_width(get_session_id())
    except TypeError:
        # Thrown if screen width is not know yet
        return False
    return width < 600


def get_session_id() -> str:
    # get session id from the current script runner thread
    return add_script_run_ctx().streamlit_script_run_ctx.session_id
