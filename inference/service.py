import logging
import os

import bentoml
import numpy as np
from PIL.Image import Image as PILImage
from bentoml.io import Image
from bentoml.io import NumpyNdarray
from fastapi import FastAPI

from publisher import ImgPublisher


def set_logging() -> None:
    loglevel = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }.get(os.getenv("BENTOML_LOGLEVEL", "INFO"))

    ch = logging.StreamHandler()
    bentoml_logger = logging.getLogger("bentoml")
    bentoml_logger.addHandler(ch)
    bentoml_logger.setLevel(loglevel)


set_logging()
multiclass_model = bentoml.onnx.get("eurygaster_multiclass_calib_dyn:latest")
binary_model = bentoml.onnx.get("eurygaster_binary_calib_dyn:latest")

providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
eurygaster_m_runner = multiclass_model.with_options(providers=providers).to_runner()
eurygaster_b_runner = binary_model.with_options(providers=providers).to_runner()
preprocessor = multiclass_model.custom_objects.get("preprocessor", None)

erg = bentoml.Service("eurygaster", runners=[eurygaster_m_runner, eurygaster_b_runner])

fastapi_app = FastAPI()
erg.mount_asgi_app(fastapi_app)

publisher = ImgPublisher()


@fastapi_app.get("/metadata")
def metadata() -> dict:
    return {
        "binary_model": binary_model.info.metadata,
        "multiclass_model": multiclass_model.info.metadata,
    }


@erg.api(input=Image(), output=NumpyNdarray())
async def classify_image(image: PILImage) -> np.ndarray:
    """
    Classify image to detect whether it has Eurygaster in it or not
    :param image: PILImage
    :return: class confidence for binary Eurygaster model
    """
    proc_img = np.expand_dims(preprocessor(image), 0)
    output = await eurygaster_b_runner.async_run(proc_img)
    return output


@erg.api(input=Image(), output=NumpyNdarray())
async def classify_eurygaster(image: PILImage) -> np.ndarray:
    """
    Classify Eurygaster spp.
    :param image: PILImage
    :return: class confidence for multiclass Eurygaster model
    """
    try:
        publisher.publish(image, "image.jpg")
    except Exception as ex:
        logging.error(f"Unexpected image publisher error:\n{ex}")
    proc_img = np.expand_dims(preprocessor(image), 0)
    output = await eurygaster_m_runner.async_run(proc_img)
    return output
