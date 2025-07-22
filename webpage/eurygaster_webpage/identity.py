import os
import requests

import streamlit as st
from urllib.parse import urlencode
from streamlit.runtime import Runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_keycloak import login

from keycloak import KeycloakOpenID
from loguru import logger

from eurygaster_webpage.structures.translations.login import LOGIN_MESSAGES


def _get_session_id():
    context = get_script_run_ctx()
    if not context:
        return
    return context.session_id


def _get_current_request():
    session_id = _get_session_id()
    if not session_id:
        return None
    runtime = Runtime._instance
    if not runtime:
        return
    client = runtime.get_client(session_id)
    if not client:
        return
    return client.request


def get_web_origin():
    request = _get_current_request()
    return request.headers["Origin"] if request else os.getenv("WEB_BASE", "")


class IdentityBroker:
    def __init__(self):
        self.auth_url = os.getenv("AUTH_URL", None)
        self.auth_realm = os.getenv("AUTH_REALM", None)
        self.auth_client = os.getenv("AUTH_CLIENT_ID", None)
        self.kc_openid = None
        self.kc_auth = None
        if "email" not in st.session_state:
            st.session_state.email = "Unknown"
        if "user_name" not in st.session_state:
            st.session_state.user_name = "Unnamed"
        if "is_authenticated" not in st.session_state:
            st.session_state.is_authenticated = False

    def sign_in(self, lang: str) -> bool:
        """
        Perform authentication process
        :param lang:
        :return: Keycloak auth object
        """
        logger.debug(
            f"Authentication:\nauth_url: {self.auth_url}\n" +
            f"auth_realm: {self.auth_realm}\n" +
            f"auth_client: {self.auth_client}"
        )
        keycloak = login(
            url=self.auth_url,
            realm=self.auth_realm,
            client_id=self.auth_client,
            custom_labels={
                "labelButton": LOGIN_MESSAGES.get(lang, "en").SIGN_IN,
                "labelLogin": LOGIN_MESSAGES.get(lang, "en").LABEL_LOGIN,
                "errorNoPopup": LOGIN_MESSAGES.get(lang, "en").ERR_NOPOPUP,
                "errorPopupClosed": LOGIN_MESSAGES.get(lang, "en").ERR_POPUPCLOSED,
                "errorFatal": LOGIN_MESSAGES.get(lang, "en").ERR_FATAL,
            },
        )
        self.kc_auth = keycloak
        if self.kc_auth.authenticated:
            self.kc_openid = KeycloakOpenID(
                server_url=self.auth_url,
                client_id=self.auth_client,
                realm_name=self.auth_realm, verify=False
            )
            st.session_state.is_authenticated = True
            st.session_state.user_name = keycloak.user_info["name"]
            st.session_state.email = keycloak.user_info["email"]
            st.session_state.keycloak_id_token = keycloak.id_token
            st.session_state.keycloak_user_info = keycloak.user_info
            logger.debug(f"Auth object: {keycloak}")
            return True
        return False

    def get_sign_out_link(self) -> str or None:
        """
        Perform logout process
        :return: None
        """
        sign_out_link = None
        if st.session_state.get("keycloak_user_info"):
            params = urlencode(
                {
                    "post_logout_redirect_uri": get_web_origin(),
                    "id_token_hint": st.session_state.keycloak_id_token,
                }
            )
            show_text = LOGIN_MESSAGES.get(st.session_state.lang).SIGN_OUT
            sign_out_link = f'<a target="_self" href="{self.auth_url}/realms/{self.auth_realm}/protocol/openid-connect/logout?{params}">{show_text}</a>'
        user_info = (st.session_state.email, st.session_state.user_name)
        logger.debug(f"User:{user_info}\nSignOut link: {sign_out_link}")
        return sign_out_link
