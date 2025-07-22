import argparse
import sentry_sdk
import streamlit as st
from eurygaster_webpage import __version__, SUPPORTED_LANG, GITHUB, ISSUES
from eurygaster_webpage.cli import parse_args
from eurygaster_webpage.identity import IdentityBroker
from eurygaster_webpage.logger import prepare_sentry
from eurygaster_webpage.pages import PlainTextPage, ModelPage, LoginPage
from eurygaster_webpage.structures.translations import titles
from eurygaster_webpage.utils import get_copyright, add_debug_settings
from loguru import logger
from requests.exceptions import ConnectionError, ConnectTimeout
from streamlit_option_menu import option_menu


def display_ui(args: argparse.Namespace, id_broker: IdentityBroker) -> None:
    pages = {
        titles.NAV_TITLES[st.session_state.lang].ABOUT: PlainTextPage(
            title=titles.MD_TITLES[st.session_state.lang].ABOUT,
            markdown_name="about.md"),
        titles.NAV_TITLES[st.session_state.lang].HOW_TO: PlainTextPage(
            title=titles.MD_TITLES[st.session_state.lang].HOW_TO,
            markdown_name="how_to_use.md"),
        titles.NAV_TITLES[st.session_state.lang].GET_ACC_REC: PlainTextPage(
            title=titles.MD_TITLES[st.session_state.lang].GET_ACC_REC,
            markdown_name="best_photo.md"
        ),
        titles.NAV_TITLES[st.session_state.lang].IDENTIFY: ModelPage(
            title=titles.MD_TITLES[st.session_state.lang].IDENTIFY,
            backend_address=args.inference_server,
            entries_address=args.entries_server,
            binary_threshold=args.binary_threshold,
        ),
    }

    st.sidebar.title(titles.NAV_TITLES[st.session_state.lang].NAV)
    with st.sidebar:
        st.write(f"{titles.ACC_TITLES[st.session_state.lang].GREET}, {st.session_state.user_name}!")
        with st.popover(titles.ACC_TITLES[st.session_state.lang].ACC):
            st.markdown(f"{titles.ACC_TITLES[st.session_state.lang].USERNAME}: {st.session_state.user_name}")
            st.markdown(f"{titles.ACC_TITLES[st.session_state.lang].EMAIL}: {st.session_state.email}")
            sign_out_link = id_broker.get_sign_out_link()
            if sign_out_link:
                st.markdown(sign_out_link, unsafe_allow_html=True)
        selection = option_menu(None, list(pages.keys()), menu_icon="cast", default_index=0)

    selected_page = pages[selection]

    with st.sidebar.expander(f"{titles.ACC_TITLES[st.session_state.lang].HELP}..."):
        st.markdown(
            f"""
        {titles.ACC_TITLES[st.session_state.lang].VER}: {__version__}\n
        * [GitHub]({GITHUB})
        * [Bugs & suggestions]({ISSUES})
        """,
            unsafe_allow_html=True,
        )
        st.markdown(get_copyright(), unsafe_allow_html=True)

    with st.spinner(f"Loading {selection} ..."):
        selected_page.write(lang=st.session_state.lang)

    logger.debug(f"Supported languages: {SUPPORTED_LANG}")
    logger.debug(f"Selected page {selected_page} with language: {st.session_state.lang}")


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
    if 'lang' not in st.session_state:
        st.session_state.lang = "en"
    add_debug_settings()

    if not st.session_state.is_authenticated:
        st.sidebar.selectbox(
            titles.NAV_TITLES[st.session_state.lang].LANG,
            SUPPORTED_LANG,
            key="lang",
            index=SUPPORTED_LANG.index(st.session_state.lang)
        )
        login_page = LoginPage(
            title=titles.ACC_TITLES[st.session_state.lang].SIGN_IN,
            id_broker=id_broker,
            entries_address=args.entries_server
        )
        login_page.write(lang=st.session_state.lang)
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
