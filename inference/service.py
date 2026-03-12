import logging
import os
import uuid

import bentoml
import numpy as np
from PIL.Image import Image as PILImage
from bentoml.io import Image
from bentoml.io import Multipart
from bentoml.io import NumpyNdarray
from bentoml.io import Text
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


def softmax(logits: np.ndarray) -> np.ndarray:
    """Convert logits to probabilities (sum to 1)."""
    x = np.asarray(logits, dtype=np.float64)
    x = x - np.max(x, axis=-1, keepdims=True)
    exp_x = np.exp(x)
    return exp_x / exp_x.sum(axis=-1, keepdims=True)


def _get_multiclass_species_scores(probs: np.ndarray) -> dict[str, float]:
    """Build recognition dict: species name -> probability from class_map and probability vector (1d or row)."""
    class_map = multiclass_model.info.metadata.get("class_map") or {}
    index_to_species = {int(k): v for k, v in class_map.items()}
    p = np.asarray(probs, dtype=np.float64).ravel()
    return {
        index_to_species.get(i, f"class_{i}"): round(float(p[i]), 4)
        for i in range(len(p))
    }


@fastapi_app.get("/metadata")
def metadata() -> dict:
    return {
        "binary_model": binary_model.info.metadata,
        "multiclass_model": multiclass_model.info.metadata,
    }


@erg.api(input=Image(), output=NumpyNdarray())
async def classify_image(image: PILImage) -> np.ndarray:
    """
    Classify image to detect whether it has Eurygaster in it or not.
    :param image: PILImage
    :return: class probabilities (softmax) for binary Eurygaster model, shape (1, n_classes)
    """
    proc_img = np.expand_dims(preprocessor(image), 0)
    output = await eurygaster_b_runner.async_run(proc_img)
    return softmax(output)


@erg.api(
    input=Multipart(image=Image(), account=Text(), name=Text()),
    output=NumpyNdarray(),
)
async def classify_eurygaster(image: PILImage, account: str, name: str) -> np.ndarray:
    """
    Classify Eurygaster spp. Account and filename are passed as multipart fields.
    :param image: PIL Image
    :param account: user account (name or email)
    :param name: original filename
    :return: class probabilities (softmax) for multiclass Eurygaster model, shape (1, n_classes)
    """
    account = account or "unknown"
    filename = name or f"{uuid.uuid4()}.jpg"

    proc_img = np.expand_dims(preprocessor(image), 0)
    output = await eurygaster_m_runner.async_run(proc_img)
    probs = softmax(output)

    recognition = _get_multiclass_species_scores(probs)
    publisher.publish(image, filename, user=account, recognition=recognition)
    return probs
