import argparse

import sentry_sdk
import streamlit as st

from streamlit_option_menu import option_menu
from loguru import logger
from requests.exceptions import ConnectionError, ConnectTimeout

from eurygaster_webpage import __version__, SUPPORTED_LANG, GITHUB, ISSUES
from eurygaster_webpage.cli import parse_args
from eurygaster_webpage.identity import IdentityBroker
from eurygaster_webpage.logger import prepare_sentry
from eurygaster_webpage.pages import PlainTextPage, ModelPage, LoginPage
from eurygaster_webpage.utils import get_copyright


def display_ui(args: argparse.Namespace, id_broker: IdentityBroker) -> None:
    pages = {
        "About": PlainTextPage(title="About", markdown_name="about.md"),
        "How to use": PlainTextPage(title="How to use", markdown_name="how_to_use.md"),
        "Getting accurate recognition": PlainTextPage(
            title="Getting accurate recognition", markdown_name="best_photo.md"
        ),
        "Identify Eurygaster": ModelPage(
            title="Identify Eurygaster",
            backend_address=args.inference_server,
            binary_threshold=args.binary_threshold,
        ),
    }

    st.sidebar.title("Navigation")
    with st.sidebar:
        st.write(f"Welcome, {st.session_state.user_name}!")
        st.markdown(id_broker.get_logout_link(st.session_state.account_name), unsafe_allow_html=True)
        selection = option_menu(None, list(pages.keys()), menu_icon="cast", default_index=0)

    selected_page = pages[selection]
    selected_lang = st.sidebar.selectbox("Language", SUPPORTED_LANG)

    with st.sidebar.expander("About..."):
        st.markdown(
            f"""
        Version: {__version__}\n
        * [GitHub]({GITHUB})
        * [Bugs & suggestions]({ISSUES})
        """,
            unsafe_allow_html=True,
        )
        st.markdown(get_copyright(), unsafe_allow_html=True)

    with st.spinner(f"Loading {selection} ..."):
        selected_page.write(lang=selected_lang)

    logger.debug(f"Supported languages: {SUPPORTED_LANG}")
    logger.debug(f"Selected page {selected_page} with language: {selected_lang}")


def main() -> None:
    args = parse_args()
    logger.debug(f"Page management args:\n{args}")

    prepare_sentry()
    id_broker = IdentityBroker()

    st.set_page_config(
        page_title=args.tab_title,
        page_icon=args.tab_icon,
        layout="centered",
        initial_sidebar_state="auto",
    )

    if not st.session_state.is_authenticated:
        st.write("## Eurygaster spp. classification")
        login_page = LoginPage(title="Sign In", id_broker=id_broker)
        login_page.write(lang="en")

    try:
        if st.session_state.is_authenticated:
            display_ui(args, id_broker)
    except (ConnectionError, ConnectTimeout) as ex:
        logger.error(ex)
        sentry_sdk.capture_exception(ex)
        st.error(f"{ex.__class__.__name__}. Please, wait for the maintenance.")
        st.info(f"Issues on GitHub: {ISSUES}")
    except Exception as unknown_exception:
        sentry_sdk.capture_exception(unknown_exception)
        logger.error(f"Unknown exception:\n{unknown_exception}")
        st.error("Unknown exception. Please, wait for the maintenance.")
        st.info(f"Issues on GitHub: {ISSUES}")
        sentry_sdk.capture_exception(unknown_exception)


if __name__ == "__main__":
    main()
