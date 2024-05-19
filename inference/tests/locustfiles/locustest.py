import io
import os
import pathlib

import numpy as np
import requests
from PIL import Image
from locust import HttpUser, task


def get_image() -> bytes:
    with open(
        os.path.join(
            pathlib.Path(__file__).parent.parent, "eurygaster_testudinaria.jpeg"
        ),
        "rb",
    ) as f:
        real_image = f.read()
    return real_image


class AbstractUser(HttpUser):
    abstract = True
    address = "http://172.55.0.1:3000"
    real_image = get_image()
    binary_map = None
    multiclass_map = None

    def get_metadata(self) -> dict:
        headers = {
            "accept": "application/json",
        }
        response = requests.get(f"{self.address}/metadata", headers=headers)
        return response.json()

    def basic_request(self, postfix: str, image: bytes) -> dict:
        headers = {
            "accept": "application/json",
            "Content-Type": "image/icns",
        }
        response = self.client.post(
            f"{self.address}/{postfix}", headers=headers, data=image
        ).json()
        return response

    def recognize_image(self, image: bytes) -> None:
        response = self.basic_request("classify_image", image)
        conf = response[0]
        class_label = self.binary_map.get(np.argmax(conf))
        if class_label == "Eurygaster":
            response = self.basic_request("classify_eurygaster", image)

    def on_start(self):
        metadata = self.get_metadata()
        self.binary_map = {
            int(k): v for k, v in metadata["binary_model"]["class_map"].items()
        }
        self.multiclass_map = {
            int(k): v for k, v in metadata["multiclass_model"]["class_map"].items()
        }


class OneImageRequestUser(AbstractUser):
    @task
    def recognize_real_image(self):
        self.recognize_image(self.real_image)

    @task
    def recognize_random_image(self):
        arr = np.random.randn(300, 300, 3)
        img = Image.fromarray(arr.astype("uint8"), "RGB")
        byte_io = io.BytesIO()
        img.save(byte_io, "JPEG")
        self.recognize_image(byte_io.getvalue())
