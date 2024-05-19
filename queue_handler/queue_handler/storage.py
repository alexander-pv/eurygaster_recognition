import dataclasses
import io
import os
from abc import ABC, abstractmethod

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
    def save(self, image: Image, name: str) -> None:
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

    def save(self, image: bytes, name: str) -> None:
        """
        Save image to an object storage
        :param image: image, in bytes
        :param name:  image name, str
        :return: None
        """
        in_mem = io.BytesIO()
        image.save(in_mem, format="jpeg")
        in_mem.seek(0)
        self._client.upload_fileobj(in_mem, self.bucket_name, name)


@dataclasses.dataclass
class StorageTypes:
    minio: StorageSaver = MinIOSaver
    empty = None
