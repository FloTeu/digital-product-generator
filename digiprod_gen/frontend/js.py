from streamlit_js_eval import streamlit_js_eval
from functools import cache


@cache
def get_screen_width(session_id: str) -> int | None:
    """
    Return screen width by javascript call
    st_session_id is provided to ensure screen width is detected once per user (because of cache)

    raises:
        TypeError: If no screen width can be detected

    """
    # Note: Can be none, if javascript is not able to detect browser width -> will throw an exception
    screen_width = streamlit_js_eval(js_expressions='screen.width', want_output=True, key="SCR")
    return int(screen_width)

