import io
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum

import requests
import boto3

from PIL import Image
from loguru import logger


class StorageSaver(ABC):
    def __init__(self):
        self._create_client()
        self._prepare_storage()

    @abstractmethod
    def _create_client(self) -> None:
        pass

    @abstractmethod
    def _prepare_storage(self) -> None:
        pass

    @abstractmethod
    def save(
        self,
        image: Image.Image,
        name: str,
        user: str | None = None,
        recognition: dict | None = None,
    ) -> None:
        pass


class MinIOSaver(StorageSaver):
    def __init__(self):
        """
        Saver for MinIO object storage
        """
        self.bucket_name = "eurygaster-bucket"
        self.endpoint = os.getenv("MINIO_ADDR", None)
        self.access_key = os.getenv("MINIO_ACCESS_KEY", None)
        self.secret_key = os.getenv("MINIO_SECRET_KEY", None)
        super().__init__()

    def _create_client(self):
        if self.endpoint:
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            logger.info("MinIO client connected to endpoint: {}", self.endpoint)
        else:
            error_msg = "{} endpoint is empty".format(self.__class__.__name__)
            logger.error(error_msg)
            raise Exception(error_msg)

    def _prepare_storage(self) -> None:
        current_buckets = [
            element["Name"] for element in self._client.list_buckets()["Buckets"]
        ]
        logger.info("Existing buckets: {}", current_buckets)
        if self.bucket_name not in current_buckets:
            self._client.create_bucket(Bucket=self.bucket_name)
            logger.info("Created bucket: {}", self.bucket_name)
        else:
            logger.debug("Bucket already exists: {}", self.bucket_name)

    def save(
        self,
        image: Image.Image,
        name: str,
        user: str | None = None,
        recognition: dict | None = None,
    ) -> None:
        """
        Save image to an object storage
        :param image: image, in bytes
        :param name:  image name, str
        :param user: optional user (ignored for MinIO)
        :param recognition: optional recognition dict (ignored for MinIO)
        :return: None
        """
        in_mem = io.BytesIO()
        image.save(in_mem, format="jpeg")
        in_mem.seek(0)
        size_bytes = in_mem.getbuffer().nbytes
        logger.debug("Uploading to MinIO: name={} size={} bytes bucket={}", name, size_bytes, self.bucket_name)
        self._client.upload_fileobj(in_mem, self.bucket_name, name)
        logger.info("MinIO upload completed: name={} size={} bytes", name, size_bytes)


class TelegramGroupSaver(StorageSaver):

    def __init__(self):
        """
        Saver for Telegram group: sends image then a JSON message with user, original_name, utc, recognition.
        """
        self.token = os.getenv("TG_BOT_TOKEN", None)
        self.group_id = os.getenv("TG_GROUP_ID", None)
        self.url_photo = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        self.url_message = f"https://api.telegram.org/bot{self.token}/sendMessage"
        super().__init__()

    def _create_client(self):
        if self.token and self.group_id:
            logger.info("Telegram saver configured: group_id={}", self.group_id)
        else:
            logger.warning("Telegram token or group_id missing")

    def _prepare_storage(self) -> None:
        pass

    def save(
        self,
        image: Image.Image,
        name: str,
        user: str | None = None,
        recognition: dict | None = None,
    ) -> None:
        """
        Send image to Telegram group, then a JSON message with user, original_name, utc, recognition (species: score).
        """
        logger.debug("Sending to Telegram: name={} user={}", name, user or "unknown")
        try:
            with io.BytesIO() as in_mem:
                image.save(in_mem, format="jpeg")
                in_mem.seek(0)
                size_bytes = in_mem.getbuffer().nbytes
                files = {"photo": (name, in_mem)}
                data = {"chat_id": self.group_id, "caption": "Received image. Name: {}".format(name)}
                response = requests.post(self.url_photo, files=files, data=data)
                response.raise_for_status()
                logger.info("Telegram photo sent: name={} size={} bytes status={}", name, size_bytes, response.status_code)

            payload = {
                "user": user or "unknown",
                "original_name": name,
                "utc": datetime.now(timezone.utc).isoformat(),
                "recognition": recognition or {},
            }
            resp = requests.post(
                self.url_message,
                json={"chat_id": self.group_id, "text": json.dumps(payload, ensure_ascii=False)},
            )
            resp.raise_for_status()
            logger.info("Telegram metadata sent: name={} status={}", name, resp.status_code)
        except Exception as e:
            logger.exception("Failed to send image {!r} to Telegram: {}", name, e)


class StorageType(Enum):
    """Supported storage backends. Value is the saver class to instantiate, or None for empty."""

    minio = MinIOSaver
    telegram = TelegramGroupSaver
    empty = None

    @classmethod
    def _missing_(cls, value: object):
        """Allow lookup by name from string (e.g. StorageType('minio'))."""
        if isinstance(value, str):
            return cls._member_map_.get(value.lower())
        return None
