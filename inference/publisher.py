import asyncio
import datetime
import logging
import os
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Any

import aio_pika
import nest_asyncio
import numpy as np
import pyarrow as pa
from PIL.Image import Image as PILImage

nest_asyncio.apply()


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
    def __init__(self):
        self.topic = os.getenv("RMQ_TOPIC", "NewImages")
        self.conn_str = os.getenv("RMQ_ADDR", None)
        self._conn = None

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
            logging.info(f"Opened RMQ connection")
            yield self._conn
        finally:
            if self._conn:
                await self._conn.close()
                logging.info(f"Closed RMQ connection")

    async def _publish(self, img: PILImage, name: str) -> None:
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
        logging.info(f"Published image: {name}")

    def publish(self, img: PILImage, name: str):
        """
        :param img:
        :param name:
        :return:
        """
        if self.conn_str:
            asyncio.run(self._publish(img, name))
        else:
            logging.warning(f"Empty connection string: {self.conn_str}")
