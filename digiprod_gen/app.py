import click
import streamlit as st
import streamlit.web.bootstrap as st_bootstrap

from io import TextIOWrapper
from digiprod_gen.backend.utils.decorators import timeit
from digiprod_gen.backend.utils import init_environment, initialise_config
from digiprod_gen.backend.models.session import SessionState
from digiprod_gen.backend.models.config import DigiProdGenConfig
from digiprod_gen.frontend.session import read_session, update_mba_request, init_session_state
from digiprod_gen.frontend.sidebar import display_page_navigation


@timeit
def display_sidebar(session_state: SessionState):
    """Renders sidebar elements based on session data"""
    sidebar_element = session_state.views.get_or_create_sidebar()
    # before re rendering, empty all existing views
    sidebar_element.empty()

    with sidebar_element.container():
        display_page_navigation()


def main(config: DigiProdGenConfig):
    init_environment()
    init_session_state(config)

    st.header("MBA Product Generator")
    session_state: SessionState = st.session_state["session_state"]

    # display views (+ add defaults to session)
    display_sidebar(session_state)

    # init session request
    if session_state.crawling_request == None:
        update_mba_request()


@click.command()
@click.option("-c", "--config", default="config/app-config.yaml", type=click.Path(exists=True))
def start_digiprod_gen(config: TextIOWrapper):
    if st.runtime.exists():
        # The app has been executed with `streamlit run app.py`
        config_obj: DigiProdGenConfig = initialise_config(
            config_file_path=config
        )
        main(config=config_obj)
    else:
        # If the file has been executed with python (`python app.py`), the streamlit functionality
        # won't work. This line reruns the app within the streamlit context, as if it has been
        # executed with `streamlit run app.py`.
        # This is necessary when installing this project from a .whl package, since the executable
        # only gets execute by python and not by streamlit.
        args: list[str] = [config]

        st_bootstrap.run(
            __file__,
            command_line="",
            args=args,
            flag_options={},
        )

if __name__ == "__main__":
    start_digiprod_gen()