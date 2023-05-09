import os
from abc import abstractmethod, ABCMeta
from typing import Optional, Union

import numpy as np
import plotly.graph_objects as go
import requests
import streamlit as st
from eurygaster_webpage import ROOT
from eurygaster_webpage import utils
from eurygaster_webpage.info.structures.hints import HINT_MESSAGES, DefaultMsg
from loguru import logger
from scipy.special import softmax
from streamlit.elements.file_uploader import SomeUploadedFiles


class Page(metaclass=ABCMeta):
    def __init__(self, title: str, markdown_name: Optional[str] = None):
        """
        Abstract class for streamlit pages
        :param title:         str, page title
        :param markdown_name: Optional[str], name of the markdown file to write
        """
        self.title = title
        self.markdown_name = markdown_name
        self.markdown_text = self.load_markdown("en")

    def load_markdown(self, lang: str) -> str:
        """
        Load markdown file
        :param lang: directory of the text for a specific language
        :return: str
        """
        if self.markdown_name:
            with open(
                    os.path.join(ROOT, "info/markdown", lang, self.markdown_name),
                    "r",
                    encoding="utf8",
            ) as f:
                text = "".join(f.readlines())
        else:
            text = None
        return text

    def set_title(self) -> None:
        """
        Set title for a streamlit page
        :return: None
        """
        st.write(f"## Eurygaster spp. classification - {self.title}")

    @staticmethod
    def hide_style() -> None:
        """
        Hide streamlit style
        :return: None
        """
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    @abstractmethod
    def write(self, lang: str) -> None:
        """
        Write page
        :param lang: str, language of the text
        :return: None
        """
        return


class PlainTextPage(Page):
    def __init__(self, *args, **kwargs):
        """
        Streamlit page with text information about the project
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

    def write(self, lang: str) -> None:
        with st.spinner(f"Loading {self.title} ..."):
            self.markdown_text = self.load_markdown(lang=lang)
            self.set_title()
            if self.markdown_text:
                st.markdown(self.markdown_text, unsafe_allow_html=True)
            self.hide_style()


class LoginPage(Page):
    def __init__(self, id_broker: object, *args, **kwargs):
        """
        Streamlit page with login
        :param id_broker: Identity broker
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.id_broker = id_broker

    def write(self, lang: str) -> None:
        with st.spinner(f"Loading {self.title} ..."):
            self.set_title()
            self.hide_style()
            self.id_broker.get_auth(lang)
            if "is_authenticated" in st.session_state:
                if st.session_state.is_authenticated:
                    st.write(f"Welcome, {self.id_broker.account_name}!")


class ModelPage(Page):
    def __init__(self, backend_address: str, binary_threshold: float, *args, **kwargs):
        """
        Streamlit page with models inference
        :param backend_address:
        :param binary_threshold:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.backend_address = backend_address
        self.binary_threshold = binary_threshold
        self._messages = HINT_MESSAGES
        self._download_types = ["jpg", "jpeg"]
        self._details_prec = 3
        self._set_class_mapping()

    def _get_metadata(self) -> dict:
        """
        Get models metadata
        :return: dict of metadata
        """
        headers = {"accept": "application/json"}
        response = requests.get(
            f"{self.backend_address}/metadata", headers=headers
        ).json()
        logger.debug(f"Metadata response:\n{response}")
        return response

    def _set_class_mapping(self) -> None:
        metadata = self._get_metadata()
        self._binary_map = {
            int(k): v for k, v in metadata["binary_model"]["class_map"].items()
        }
        self._multiclass_map = {
            int(k): v for k, v in metadata["multiclass_model"]["class_map"].items()
        }

    def _update_msg_lang(self, lang: str) -> None:
        self._cur_msg = self._messages.get(lang, DefaultMsg)

    def make_barplot(self, details: dict) -> None:
        """
        Make a barplot for confidence values
        :param details: output of the model
        :return: None
        """
        image_has_eurygaster = len(details) > 2
        if image_has_eurygaster:
            sorted_output = sorted(details.items(), key=lambda x: x[1], reverse=True)
            class_names, class_confidence = (x[0] for x in sorted_output), (
                float(x[1]) for x in sorted_output
            )
            fig = go.Figure([go.Bar(x=tuple(class_names), y=tuple(class_confidence))])
            fig.update_layout(yaxis_title="Class confidence", xaxis_title="Species")
            fig.update_traces(
                textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
            )
            st.plotly_chart(fig, use_container_width=True)

    def insert_picture(self, file: Union[SomeUploadedFiles, None]) -> None:
        if file:
            pil_image = utils.open_image(file)
            st.image(pil_image, use_column_width=True)

    def image_request(self, postfix: str, file: SomeUploadedFiles) -> dict:
        """
        Send particular image recognition request
        :param postfix:
        :param file:
        :return: dict
        """
        headers = {
            "accept": "application/json",
            "Content-Type": "image/icns",
            "Name": file.name,
        }
        endpoint = f"{self.backend_address}/{postfix}"
        response = requests.post(endpoint, headers=headers, data=file.getvalue()).json()
        logger.debug(f"image_request to {endpoint}:\n{response}")
        return response

    def classify_image(self, file: SomeUploadedFiles) -> dict:
        confidence = self.image_request("classify_image", file)[0]
        confidence = softmax(confidence).ravel()
        binary_confidence, class_id = max(confidence), np.argmax(confidence)
        binary_label = self._binary_map.get(class_id)
        if binary_label == "Eurygaster" and binary_confidence > self.binary_threshold:
            confidence_cls = self.image_request("classify_eurygaster", file)[0]
            confidence_cls = softmax(confidence_cls).ravel()
            class_label = self._multiclass_map.get(np.argmax(confidence_cls))
            class_confidence = max(confidence_cls)
            st.info(self._cur_msg.RECOGNIZED_AS % (class_label, class_confidence))
            details = {
                self._multiclass_map[i]: round(confidence_cls[i], self._details_prec)
                for i in range(len(self._multiclass_map))
            }
            return details
        else:
            st.info(self._cur_msg.WAS_FILTERED)
            details = {
                self._binary_map[i]: round(confidence[i], self._details_prec)
                for i in range(len(self._binary_map))
            }
            return details

    def write(self, lang: str) -> None:
        with st.spinner(f"Loading {self.title} ..."):
            self.set_title()
            self._update_msg_lang(lang)
            file = st.file_uploader(self._cur_msg.ASK_IMAGE, type=self._download_types)
            self.insert_picture(file)
            if file:
                details = self.classify_image(file)
                logger.debug(f"classify_image for file: {file.name}:\n{details}")
                st.write("Details:")
                st.json(details)
                self.make_barplot(details)
            self.hide_style()
