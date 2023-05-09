import os

from eurygaster_webpage.info.structures.login import LOGIN_MESSAGES
from keycloak import KeycloakOpenID
from loguru import logger
from streamlit_keycloak import login, Keycloak
import streamlit as st


class IdentityBroker:
    def __init__(self):
        self.auth_url = os.getenv("AUTH_URL", None)
        self.auth_realm = os.getenv("AUTH_REALM", None)
        self.auth_client = os.getenv("AUTH_CLIENT_ID", None)
        self.kc_openid = None
        self.kc_auth = None
        self.account_name = "unknown"
        if "is_authenticated" not in st.session_state:
            st.session_state.is_authenticated = False

    def _reset(self) -> None:
        self.kc_auth = None
        self.kc_openid = None
        self.account_name = "unknown"
        st.session_state.is_authenticated = False

    def get_auth(self, lang: str) -> Keycloak:
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
            self.account_name = keycloak.user_info["preferred_username"]
            logger.debug(f"Auth object: {keycloak}")

    def logout(self) -> None:
        """
        Perform logout process
        :return: None
        """
        self.kc_openid.logout(self.kc_auth.refresh_token)
        self._reset()
        logger.debug(f"Logged out")
