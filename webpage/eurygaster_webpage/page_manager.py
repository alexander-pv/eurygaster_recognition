import sentry_sdk
import streamlit as st
from eurygaster_webpage import __version__, SUPPORTED_LANG, GITHUB, ISSUES
from eurygaster_webpage.cli import parse_args
from eurygaster_webpage.identity import IdentityBroker
from eurygaster_webpage.logger import prepare_sentry
from eurygaster_webpage.pages import PlainTextPage, ModelPage, LoginPage
from loguru import logger
from requests.exceptions import ConnectionError, ConnectTimeout

prepare_sentry()
id_broker = IdentityBroker()


def main():
    args = parse_args()
    logger.debug(f"Page management args:\n{args}")
    st.set_page_config(
        page_title=args.tab_title,
        page_icon=args.tab_icon,
        layout="centered",
        initial_sidebar_state="auto",
    )
    pages = {
        "Login": LoginPage(title="Login", id_broker=id_broker),
        "About": PlainTextPage(title="About", markdown_name="about.md"),
        "How to use": PlainTextPage(title="How to use", markdown_name="how_to_use.md"),
        "Getting accurate recognition": PlainTextPage(
            title="Getting accurate recognition", markdown_name="best_photo.md"
        ),
        "Model": ModelPage(
            title="Model",
            backend_address=args.inference_server,
            binary_threshold=args.binary_threshold,
        ),
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Sections", list(pages.keys()))
    selected_page = pages[selection]
    logger.debug(f"Supported languages: {SUPPORTED_LANG}")
    selected_lang = st.sidebar.selectbox("Language", SUPPORTED_LANG)
    logger.debug(f"Selected page {selected_page} with language: {selected_lang}")

    with st.sidebar.expander("More..."):
        st.markdown(
            f"""
        Web version: "{__version__}"\n
        * [GitHub]({GITHUB})
        * [Report a bug]({ISSUES})
        """,
            unsafe_allow_html=True,
        )

    with st.spinner(f"Loading {selection} ..."):
        logger.debug(f"id_broker.is_authenticated: {st.session_state.is_authenticated}, selection: {selection}")
        can_render = st.session_state.is_authenticated or selection == "Login"
        if can_render:
            selected_page.write(lang=selected_lang)
        else:
            st.info('You need to login to proceed')


if __name__ == "__main__":

    try:
        main()
    except (ConnectionError, ConnectTimeout) as ex:
        logger.error(ex)
        sentry_sdk.capture_exception(ex)
        st.error(f"{ex.__class__.__name__}. Please, wait for the maintenance.")
        st.info(f"Issues on GitHub: {ISSUES}")
    except Exception as unkwn_ex:
        sentry_sdk.capture_exception(unkwn_ex)
        logger.error(f"Unknown exception:\n{unkwn_ex}")
        st.error("Unknown exception. Please, wait for the maintenance.")
        st.info(f"Issues on GitHub: {ISSUES}")
        sentry_sdk.capture_exception(unkwn_ex)
