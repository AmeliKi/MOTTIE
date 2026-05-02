"""Project-wide helpers (filenames, image preprocessing)."""

from __future__ import annotations

import logging
import os
from datetime import datetime

import cv2
import numpy as np
from PIL import Image

from config import FILENAME_PREFIX

logger = logging.getLogger(__name__)


def create_filename(prefix: str | None = None, directory: str | None = None) -> str:
    """Build a timestamped PNG filename.

    Args:
        prefix:    Filename prefix; falls back to `config.FILENAME_PREFIX`.
        directory: Optional directory; created if it does not exist. When given,
                   the returned path is `<directory>/<prefix>_<timestamp>.png`.
    """
    name = "{}_{}.png".format(prefix or FILENAME_PREFIX, datetime.now().strftime("%Y%m%d%H%M%S"))
    if directory:
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, name)
    return name


def remove_local_file(filename: str) -> None:
    """Delete `filename`, swallowing missing-file errors."""
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
    except OSError:
        logger.exception("Failed to remove %s", filename)


# --- Image preprocessing helpers (used by the TensorFlow / ONNX pipelines) ---

def convert_to_opencv(image: Image.Image) -> np.ndarray:
    """Convert a PIL image (RGB) to an OpenCV-style BGR numpy array."""
    image = image.convert("RGB")
    r, g, b = np.array(image).T
    return np.array([b, g, r]).transpose()


def crop_center(img: np.ndarray, cropx: int, cropy: int) -> np.ndarray:
    """Crop the centred (cropx × cropy) region from `img`."""
    h, w = img.shape[:2]
    startx = w // 2 - (cropx // 2)
    starty = h // 2 - (cropy // 2)
    return img[starty:starty + cropy, startx:startx + cropx]


def resize_down_to_max_dim(image: np.ndarray, max_dim: int = 1600) -> np.ndarray:
    """Downscale so the largest side equals `max_dim`, preserving aspect ratio."""
    h, w = image.shape[:2]
    if h < max_dim and w < max_dim:
        return image
    new_size = (max_dim * w // h, max_dim) if (h > w) else (max_dim, max_dim * h // w)
    return cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)


def resize_to_square(image: np.ndarray, side: int = 256) -> np.ndarray:
    """Resize to a (side × side) square."""
    return cv2.resize(image, (side, side), interpolation=cv2.INTER_LINEAR)


# EXIF orientation tag (JEITA CP-3451): rotates/flips the image into the
# orientation the camera intended.
_EXIF_ORIENTATION_TAG = 0x0112


def update_orientation(image: Image.Image) -> Image.Image:
    """Apply EXIF orientation, if present, so the image is upright."""
    if not hasattr(image, "_getexif"):
        return image
    exif = image._getexif()
    if not exif or _EXIF_ORIENTATION_TAG not in exif:
        return image
    orientation = exif.get(_EXIF_ORIENTATION_TAG, 1) - 1
    if orientation >= 4:
        image = image.transpose(Image.TRANSPOSE)
    if orientation in (2, 3, 6, 7):
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    if orientation in (1, 2, 5, 6):
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    return image
