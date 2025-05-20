import base64
from datetime import datetime
from io import BytesIO
from typing import Union

from PIL import Image, UnidentifiedImageError
from PIL.JpegImagePlugin import JpegImageFile
from streamlit.elements.widgets.file_uploader import SomeUploadedFiles


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


def get_copyright() -> str:
    copyright = f"""\n\n<left>
    © 2021-{datetime.now().year}<br/>
    The Zoological Institute RAS (ZISP)<br/>
    Designed by A. Popkov<br/>
    Text V. Neimorovets</left>
    """
    return copyright
