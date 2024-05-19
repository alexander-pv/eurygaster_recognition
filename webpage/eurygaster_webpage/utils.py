from typing import Union
from datetime import datetime
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


def get_copyright() -> str:
    copyright = f"""\n\n<left>
    © 2021-{datetime.now().year}<br/>
    The Zoological Institute RAS (ZISP)<br/>
    Designed by A. Popkov<br/>
    Text V. Neimorovets</left>
    """
    return copyright
