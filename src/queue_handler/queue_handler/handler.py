import asyncio
import dataclasses
import os
import pickle
import sys
from contextlib import asynccontextmanager

import aio_pika
import numpy as np
from PIL import Image
from aio_pika.exceptions import AMQPConnectionError
from aio_pika.queue import AbstractQueue
from loguru import logger
from queue_handler.storage import StorageType


def deserialize(msg: bytes) -> object:
    """Deserialize message bytes (pickle; matches inference publisher)."""
    return pickle.loads(msg)


@dataclasses.dataclass
class QueueMessage:
    image: bytes
    name: str
    shape: tuple
    user: str | None = None
    recognition: dict | None = None


class QueueHandler:
    def __init__(self):
        """
        Queue handler that takes images from message broker topic `self.topic` and sends them to storage via
        """
        self.topic = os.getenv("RMQ_TOPIC", "NewImages")
        self.conn_str = self._get_conn_string()
        self.saver = self._get_saver()
        storage_type = os.getenv("STORAGE_TYPE", "empty")
        logger.info("QueueHandler initialized: topic={} storage={}", self.topic, storage_type)

    def _get_conn_string(self) -> str:
        conn_str = os.getenv("RMQ_ADDR", None)
        if conn_str is None:
            error_msg = "RMQ_ADDR env variable not found"
            logger.error(error_msg)
            raise Exception(error_msg)
        logger.debug("RMQ connection string configured (host hidden)")
        return conn_str

    def _get_saver(self):
        storage_type = os.getenv("STORAGE_TYPE", "empty")
        try:
            kind = StorageType(storage_type)
        except ValueError:
            error_msg = "STORAGE_TYPE env variable not found or invalid"
            logger.error("{} (current: {!r}). Valid: {}", error_msg, storage_type, [m.name for m in StorageType])
            raise Exception(error_msg)
        if kind.value is None:
            error_msg = "STORAGE_TYPE must not be 'empty'"
            logger.error(error_msg)
            raise Exception(error_msg)
        logger.debug("Storage saver resolved: {}", storage_type)
        return kind.value()

    @asynccontextmanager
    async def connection(self) -> aio_pika.Connection:
        """
        Message broker connection async context manager
        :return: aio_pika.Connection
        """
        self._conn = None
        try:
            logger.info("Connecting to message broker...")
            self._conn = await aio_pika.connect_robust(self.conn_str)
            self._channel = await self._conn.channel()
            self._exchange = await self._channel.declare_exchange(
                self.topic, aio_pika.ExchangeType.TOPIC
            )
            logger.info("Subscribed to RMQ topic: {}", self.topic)
            yield self._conn
        except AMQPConnectionError as con_err:
            logger.error("AMQP connection failed: {}", con_err)
            sys.exit(con_err)
        finally:
            if self._conn:
                logger.info("Closing RMQ connection")
                await self._conn.close()
                sys.exit("Closed RMQ connection")

    async def run(self):
        async with self.connection():
            queue = await self._channel.declare_queue("", exclusive=True)
            await queue.bind(self._exchange, routing_key="image")
            logger.info("Queue bound with routing_key=image, waiting for messages")
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
                    try:
                        body = deserialize(message.body)
                    except Exception as e:
                        logger.exception("Failed to deserialize message body: {}", e)
                        continue
                    if not isinstance(body, dict):
                        logger.warning("Queue message body is not a dict, type={}", type(body).__name__)
                    else:
                        rec_keys = list((body.get("recognition") or {}).keys())
                        logger.debug(
                            "Queue message keys: {} | name={!r} | user={!r} | shape={!r} | recognition keys={!r}",
                            list(body.keys()), body.get("name"), body.get("user"), body.get("shape"), rec_keys,
                        )
                    msg = QueueMessage(
                        image=body["image"],
                        name=body["name"],
                        shape=body["shape"],
                        user=body.get("user"),
                        recognition=body.get("recognition"),
                    )
                    user_display = msg.user if msg.user is not None else "unknown"
                    logger.info(
                        "Received message: name={!r} user={!r} shape={} recognition_count={}",
                        msg.name, user_display, msg.shape, len(msg.recognition or {}),
                    )
                    try:
                        arr = np.frombuffer(msg.image, dtype=np.uint8).reshape(msg.shape)
                        img = Image.fromarray(arr, mode="RGB")
                        self.saver.save(img, msg.name, user=msg.user, recognition=msg.recognition)
                        logger.info("Sent to storage: {}", msg.name)
                    except Exception as e:
                        logger.exception("Failed to save message {!r}: {}", msg.name, e)

    def start(self) -> None:
        """
        Main method with asyncio mainloop
        :return: None
        """
        loop = asyncio.get_event_loop()
        try:
            logger.info("Starting asyncio event loop")
            asyncio.ensure_future(self.run())
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Asyncio loop interrupted (KeyboardInterrupt)")
        finally:
            loop.close()
            logger.info("Asyncio loop closed")
