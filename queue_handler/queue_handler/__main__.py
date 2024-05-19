import os

import sentry_sdk
from loguru import logger
from queue_handler.handler import QueueHandler
from queue_handler.logger import prepare_logger, prepare_sentry

from queue_handler import LIBNAME


def main() -> None:
    QueueHandler().start()


if __name__ == "__main__":
    prepare_logger(
        LIBNAME, os.getenv("LOGURU_LEVEL", "DEBUG"), os.getenv("LOGURU_INIT", True)
    )
    prepare_sentry()
    try:
        main()
    except Exception as unkwn_ex:
        sentry_sdk.capture_exception(unkwn_ex)
        logger.error(f"Unknown exception:\n{unkwn_ex}")
        sentry_sdk.capture_exception(unkwn_ex)
