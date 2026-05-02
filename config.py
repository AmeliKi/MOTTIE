"""Centralised configuration loaded from environment variables.

Values are read from the process environment, populated by `python-dotenv`
from a local `.env` file (see `.env.example` for the expected schema).
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# --- Azure IoT Hub ---
IOT_HUB_CONNECTION_STRING = os.getenv("IOT_HUB_CONNECTION_STRING", "")

# --- Azure Storage / Data Lake ---
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY", "")
STORAGE_ACCOUNT_CONTAINER_NAME = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME", "mothcam")
STORAGE_ACCOUNT_DIRECTORY_NAME = os.getenv("STORAGE_ACCOUNT_DIRECTORY_NAME", "upload")

# --- Camera / image defaults ---
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "2312"))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1736"))
IMAGE_FORMAT = os.getenv("IMAGE_FORMAT", "RGB888")
FILENAME_PREFIX = os.getenv("FILENAME_PREFIX", "moth")

# --- Behaviour flags ---
ENABLE_IOT = _bool(os.getenv("ENABLE_IOT"), default=True)
ENABLE_INFERENCE = _bool(os.getenv("ENABLE_INFERENCE"), default=False)
