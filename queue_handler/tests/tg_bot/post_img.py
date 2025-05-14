import os

import requests
from loguru import logger

IMAGE_PATH = 'test.png'


class TelegramGroupSaver:

    def __init__(self):
        self.token = os.getenv("TG_BOT_TOKEN", None)
        self.group_id = os.getenv("TG_GROUP_ID", None)
        self.url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        super().__init__()

    def _create_client(self):
        pass

    def _prepare_storage(self) -> None:
        pass

    def save(self) -> None:
        try:
            with open(IMAGE_PATH, 'rb') as f:
                files = {'photo': f}
                data = {
                    'chat_id': self.group_id,
                    'caption': 'Received image. Name: {}. Datetime: {}'
                }
                response = requests.post(self.url, files=files, data=data)
                logger.info(f"response: {response}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")


def test_send_img():
    saver = TelegramGroupSaver()
    saver.save()


if __name__ == "__main__":
    test_send_img()
