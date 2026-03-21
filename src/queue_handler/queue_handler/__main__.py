import os

from loguru import logger
from queue_handler.handler import QueueHandler
from queue_handler.logger import prepare_logger

from queue_handler import LIBNAME


def main() -> None:
    QueueHandler().start()


if __name__ == "__main__":
    prepare_logger(
        LIBNAME, os.getenv("LOGURU_LEVEL", "DEBUG"), os.getenv("LOGURU_INIT", "1")
    )
    logger.info(
        "Starting queue handler: topic={} storage={}",
        os.getenv("RMQ_TOPIC", "NewImages"),
        os.getenv("STORAGE_TYPE", "empty"),
    )
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutdown requested (KeyboardInterrupt)")
    except Exception as unkwn_ex:
        logger.exception("Unhandled exception: {}", unkwn_ex)
        raise
