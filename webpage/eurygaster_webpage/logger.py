import os
import sys

import sentry_sdk
from loguru import logger


def prepare_logger(lib_name: str, level: str, init: str or bool) -> logger:
    """
    Prepare general Loguru loggers
    :param lib_name: str, library name
    :param level: str, loguru logging level
    :param init: str or bool, init library logging or not
    :return: object loguru_logger
    """
    try:
        user = os.getlogin()
    except OSError:
        user = f"{lib_name}_containerized"

    try:
        init = bool(int(init))
    except ValueError:
        logger.warning(
            f"Expected int logging env variable. Got: {init}. init was switched to default value."
        )
    finally:
        logger.warning(f"Variable 'init' is: {init}")

    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                + "<level>{level}</level> | "
                + "<cyan>{name}:{function}:{line}</cyan> - "
                + "{message}",
                "level": level,
            }
        ],
        "extra": {"user": user},
    }
    logger.configure(**config)

    if init:
        logger.info(f"Logger init. Level: {level}")
        logger.enable(lib_name)
    else:
        logger.info(f"Logging is disabled.")
        logger.disable(lib_name)
    return logger


def prepare_sentry() -> None:
    if os.getenv("GLITCHTIP_DSN"):
        sentry_sdk.init(
            dsn=os.getenv("GLITCHTIP_DSN"),
            max_breadcrumbs=int(os.getenv("GLITCHTIP_MAX_BREADCRUMBS", 50)),
            debug=bool(os.getenv("GLITCHTIP_DEBUG", 0)),
            traces_sample_rate=float(os.getenv("GLITCHTIP_SR", 1.0)),
        )
