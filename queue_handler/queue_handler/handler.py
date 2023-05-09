import asyncio
import dataclasses
import os
import sys
from contextlib import asynccontextmanager

import aio_pika
import numpy as np
import pyarrow as pa
from PIL import Image
from aio_pika.exceptions import AMQPConnectionError
from aio_pika.queue import AbstractQueue
from loguru import logger
from queue_handler.storage import StorageTypes


def deserialize(msg: bytes) -> object:
    """
    :param msg: bytes
    :return: deserialized python object
    """
    return pa.deserialize(msg)


@dataclasses.dataclass
class QueueMessage:
    image: bytes
    name: str
    shape: tuple


class QueueHandler:
    def __init__(self):
        """
        Queue handler that takes images from message broker topic `self.topic` and sends them to storage via
        """
        self.topic = os.getenv("RMQ_TOPIC", "NewImages")
        self.conn_str = self._get_conn_string()
        self.saver = self._get_saver()

    def _get_conn_string(self) -> str:
        conn_str = os.getenv("RMQ_ADDR", None)
        if conn_str is None:
            error_msg = "RMQ_ADDR env variable not found"
            logger.error(error_msg)
            raise Exception(error_msg)
        return conn_str

    def _get_saver(self):
        saver = getattr(StorageTypes, os.getenv("STORAGE_TYPE", "empty"))
        if saver is None:
            error_msg = "STORAGE_TYPE env variable not found"
            logger.error(error_msg)
            raise Exception(error_msg)
        return saver()

    @asynccontextmanager
    async def connection(self) -> aio_pika.Connection:
        """
        Message broker connection async context manager
        :return: aio_pika.Connection
        """
        self._conn = None
        try:
            self._conn = await aio_pika.connect_robust(self.conn_str)
            self._channel = await self._conn.channel()
            self._exchange = await self._channel.declare_exchange(
                self.topic, aio_pika.ExchangeType.TOPIC
            )
            logger.info(f"Subscribed to RMQ topic: {self.topic}")
            yield self._conn
        except AMQPConnectionError as con_err:
            logger.error(f"{con_err}")
            sys.exit(con_err)
        finally:
            if self._conn:
                await self._conn.close()
                msg = "Closed RMQ connection"
                logger.info(msg)
                sys.exit(msg)

    async def run(self):
        async with self.connection():
            queue = await self._channel.declare_queue("", exclusive=True)
            await queue.bind(self._exchange, routing_key="image")
            await self._run(queue)

    async def _run(self, queue: AbstractQueue) -> None:
        """
        Run to retrieve and send images to storage
        :param queue: AbstractQueue
        :return: None
        """
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    msg = QueueMessage(**deserialize(message.body))
                    logger.info(f"Received message with file: {msg.name}")
                    arr = np.frombuffer(msg.image, dtype=np.uint8).reshape(msg.shape)
                    img = Image.fromarray(arr, mode="RGB")
                    self.saver.save(img, msg.name)
                    logger.info(f"Sent to storage: {msg.name}")

    def start(self) -> None:
        """
        Main method with asyncio mainloop
        :return: None
        """
        loop = asyncio.get_event_loop()
        try:
            asyncio.ensure_future(self.run())
            loop.run_forever()
        except KeyboardInterrupt as ex:
            logger.error(f"{ex}")
        finally:
            loop.close()
            logger.info("Asyncio loop is closed")
