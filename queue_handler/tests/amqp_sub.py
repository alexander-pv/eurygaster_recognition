import asyncio
import dataclasses

import aio_pika
import numpy as np
import pyarrow as pa
from PIL import Image

CONN_STRING = "amqp://user:password@127.0.0.1:5672"
TOPIC = "NewImage"


@dataclasses.dataclass
class RMQMessage:
    image: bytes
    name: str
    shape: tuple


def deserialize(msg: bytes) -> object:
    return pa.deserialize(msg)


async def consume_image() -> None:
    connection = await aio_pika.connect_robust(CONN_STRING)
    channel = await connection.channel()
    print(f"Connected to: {CONN_STRING}")
    exchange = await channel.declare_exchange(TOPIC, aio_pika.ExchangeType.TOPIC)

    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind(exchange, routing_key="image")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print("Received message")
                msg = RMQMessage(**deserialize(message.body))
                arr = np.frombuffer(msg.image, dtype=np.uint8).reshape(msg.shape)
                img = Image.fromarray(arr, mode="RGB")
                img.save(msg.name)


if __name__ == "__main__":
    asyncio.run(consume_image())
