import dataclasses
import io
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone

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
            logger.info(f"Client connected to storage")
        else:
            error_msg = f"{self.__class__.__name__} endpoint is empty"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _prepare_storage(self) -> None:
        current_buckets = [
            element["Name"] for element in self._client.list_buckets()["Buckets"]
        ]
        logger.info(f"Existing user buckets:{current_buckets}")
        if self.bucket_name not in current_buckets:
            self._client.create_bucket(Bucket=self.bucket_name)
            logger.info(f"Created new bucket: {self.bucket_name}")
        else:
            logger.info(f"Bucket: {self.bucket_name} already exists")

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
        self._client.upload_fileobj(in_mem, self.bucket_name, name)


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
        pass

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
        try:
            with io.BytesIO() as in_mem:
                image.save(in_mem, format="jpeg")
                in_mem.seek(0)
                files = {"photo": (name, in_mem)}
                data = {"chat_id": self.group_id, "caption": f"Received image. Name: {name}"}
                response = requests.post(self.url_photo, files=files, data=data)
                response.raise_for_status()
                logger.info(f"Telegram photo response: {response}")

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
            logger.info(f"Telegram metadata response: {resp}")
        except Exception as e:
            logger.error(f"Failed to send image {name}: {str(e)}", exc_info=True)


@dataclasses.dataclass
class StorageTypes:
    minio: StorageSaver = MinIOSaver
    telegram: StorageSaver = TelegramGroupSaver
    empty = None
