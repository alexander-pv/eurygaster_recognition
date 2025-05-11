import asyncio
import datetime
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Any

import aio_pika
import numpy as np
import pyarrow as pa
from PIL import Image as PILImage

CONN_STRING = "amqp://user:password@127.0.0.1:5672"
TOPIC = "NewImage"


def pil_to_array(img: PILImage) -> np.ndarray:
    return np.array(img)


def serialize(obj: Any) -> bytes:
    """
    :param obj:
    :return:
    """
    bytes_io = BytesIO()
    pa.serialize(obj).write_to(bytes_io)
    return bytes_io.getbuffer().tobytes()


class ImgPublisher:
    def __init__(self, topic: str, con_str: str):
        self.topic = topic
        self.conn_str = con_str

    @asynccontextmanager
    async def connection(self) -> aio_pika.Connection:
        """
        :return:
        """
        try:
            self._conn = await aio_pika.connect_robust(self.conn_str)
            self._channel = await self._conn.channel()
            self._exchange = await self._channel.declare_exchange(
                self.topic, aio_pika.ExchangeType.TOPIC
            )
            print(f"Opened RMQ connection")
            yield self._conn
        finally:
            await self._conn.close()
            print(f"Closed RMQ connection")

    async def _publish(self, img, name: str):
        async with self.connection():
            timestamp = str(int(datetime.datetime.now().timestamp()))
            arr = pil_to_array(img)
            msg = {
                "image": arr.tobytes(),
                "shape": arr.shape,
                "name": f"{timestamp}_{name}",
            }
            await self._exchange.publish(
                aio_pika.Message(
                    body=serialize(msg),
                    content_type="image/jpeg",
                    headers={"filename": f"{timestamp}_{name}"},
                ),
                routing_key="image",
            )
        print(f"Published image: {name}")

    def publish(self, img, name: str):
        """
        :param img:
        :param name:
        :return:
        """
        if self.conn_str:
            asyncio.run(self._publish(img, name))
        else:
            print(f"Empty connection string: {self.conn_str}")


if __name__ == "__main__":
    test_image = np.random.randn(2, 2, 3).astype(np.uint8)
    img_shape = test_image.shape
    test_name = "image.jpg"
    publisher = ImgPublisher(TOPIC, CONN_STRING)
    publisher.publish(PILImage.fromarray(test_image, mode="RGB"), "test.jpg")
    print(f"Published image:\n{test_name}\n{test_image}")
