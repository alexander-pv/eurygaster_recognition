import asyncio
import datetime
import logging
import os
import pickle
from contextlib import asynccontextmanager
from typing import Any

import aio_pika
import nest_asyncio
import numpy as np
from aio_pika.exceptions import AMQPConnectionError
from PIL.Image import Image as PILImage

nest_asyncio.apply()

# Avoid ERROR logs from aio_pika/aiormq when RabbitMQ is unreachable (publish is optional)
logging.getLogger("aio_pika").setLevel(logging.WARNING)
logging.getLogger("aiormq").setLevel(logging.WARNING)


def pil_to_array(img: PILImage) -> np.ndarray:
    return np.array(img)


def serialize(obj: Any) -> bytes:
    """Serialize a message dict to bytes (pickle; pyarrow.serialize was removed in PyArrow 12+)."""
    return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)


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

    async def _publish(
        self,
        img: PILImage,
        name: str,
        user: str | None = None,
        recognition: dict | None = None,
    ) -> None:
        async with self.connection():
            timestamp = str(int(datetime.datetime.now().timestamp()))
            arr = pil_to_array(img)
            msg = {
                "image": arr.tobytes(),
                "shape": arr.shape,
                "name": f"{timestamp}_{name}",
                "user": user,
                "recognition": recognition or {},
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

    def publish(
        self,
        img: PILImage,
        name: str,
        user: str | None = None,
        recognition: dict | None = None,
    ) -> None:
        if not self.conn_str:
            logging.debug("RMQ_ADDR not set; skipping image publish")
            return
        try:
            asyncio.run(self._publish(img, name, user, recognition))
        except AMQPConnectionError as ex:
            logging.warning(
                "RabbitMQ unreachable; image not published. "
                "Set RMQ_ADDR to a reachable broker or leave unset to disable. %s",
                ex,
            )
        except (ConnectionRefusedError, OSError) as ex:
            logging.warning(
                "RabbitMQ unreachable (connection refused); image not published. %s",
                ex,
            )
        except Exception as ex:
            logging.warning("Image publish to RabbitMQ failed: %s", ex)
