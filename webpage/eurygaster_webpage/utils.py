import base64
import os
import functools
import streamlit as st
from PIL import Image, UnidentifiedImageError
from PIL.JpegImagePlugin import JpegImageFile
from datetime import datetime
from io import BytesIO
from streamlit.elements.widgets.file_uploader import SomeUploadedFiles
from typing import Union
from loguru import logger


def open_image(file: SomeUploadedFiles) -> Union[JpegImageFile, None]:
    """
    Open an image with PIL.Image
    :param file: streamlit UploadedFile
    :return: JpegImageFile or None
    """

    try:
        img = Image.open(file)
    except UnidentifiedImageError:
        img = None
    return img


def resize_image(img: Image, w: int, h: int) -> Image:
    return img.resize((w, h))


def image2base64str(img: Image) -> str:
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def image2base64str_icon(img: Image, size: int) -> str:
    return image2base64str(resize_image(img, size, size))


@functools.cache
def get_copyright() -> str:
    copyright = f"""\n\n<left>
    © 2021-{datetime.now().year}<br/>
    Designed by A. Popkov<br/>
    Text V. Neimorovets</left>
    """
    return copyright


@functools.lru_cache(maxsize=100)
def read_md(root: str, subpath: str, lang: str, filename: str) -> str:
    with open(
            os.path.join(root, subpath, lang, filename),
            "r",
            encoding="utf8",
    ) as f:
        text = "".join(f.readlines())
    return text


def add_debug_settings() -> None:
    debug_pass_auth = bool(int(os.getenv("DEBUG_PASS_AUTH", 0)))
    logger.warning(f"DEBUG_PASS_AUTH: {debug_pass_auth}")
    st.session_state.is_authenticated = debug_pass_auth
