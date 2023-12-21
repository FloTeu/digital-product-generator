from streamlit_js_eval import streamlit_js_eval


def get_screen_width() -> int | None:
    # Note: Can be none, if javascript is not able to detect browser width
    screen_width = streamlit_js_eval(js_expressions='screen.width', key='SCR')
    if screen_width is None:
        return screen_width
    return int(screen_width)

