import logging
import re
from typing import NamedTuple, Union, List
from datetime import datetime

import requests

from cli.colors import colored

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextToQR(NamedTuple):
    n0: int
    x: int
    c: str


class UploadResponse(NamedTuple):
    success: bool
    filename: str
    dir: str
    url: str
    errorMessage: Union[str, None]
    contentType: str
    size: int
    uploadedAt: datetime
    expiresAt: datetime
    jqr: dict


BASE_URL = "https://api2.qrshare.io"


class Client:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def upload(self, filename: str) -> UploadResponse:
        print(f"Uploading: {colored(filename)}...")
        with open(filename, "rb") as f:
            data = {"file": (re.split(r"/|\\", filename)[-1], f)}
            response = requests.post(f"{self.base_url}/api/upload?ddl=true", files=data)
            response_content = response.json()

            logger.debug(f"{response.status_code}\n{response_content}")

            if response.ok:
                return UploadResponse(**response_content)
            else:
                return UploadResponse(success=False, errorMessage=f"{response.status_code}: {response.reason}")

    def get_direct_download_url(self, upload_id: str) -> TextToQR:
        return f"{self.base_url}/api/v2/transfer/ddl/{upload_id}"

    def text_to_qr(self, text: str) -> TextToQR:
        response = requests.get(f"{self.base_url}/api/qr/json?text={text}").json()
        return TextToQR(**response)
