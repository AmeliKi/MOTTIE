"""Background thread that periodically captures a moth photo."""

import logging
import threading
import time

from camera import Camera
from flash import Flash
from utils import create_filename
from uv import UVLight

logger = logging.getLogger(__name__)

_IMAGES_DIR = "images"
_CAPTURE_INTERVAL_SECONDS = 300  # 5 minutes between captures.
_LOOP_IDLE_SECONDS = 2           # Brief pause to keep the CPU cool.


class Unattended(threading.Thread):
    """Capture a photo every `_CAPTURE_INTERVAL_SECONDS` until stopped."""

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self._stop_event = threading.Event()
        self._uv = UVLight()
        self._flash = Flash()

    def photo(self) -> None:
        """Capture a single photo, lit by the flash, and save it locally."""
        camera = Camera()
        filename = create_filename(directory=_IMAGES_DIR)
        try:
            self._flash.on()
            camera.take_picture(filename)
        finally:
            self._flash.off()
        logger.info("Photo saved: %s", filename)

    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._uv.on()
                # Wait for the unattended interval, but exit promptly if stopped.
                if self._stop_event.wait(_CAPTURE_INTERVAL_SECONDS):
                    break
                self._uv.off()
                self.photo()
            except Exception:
                logger.exception("Unattended cycle failed; stopping thread")
                self.stop()
                return
            time.sleep(_LOOP_IDLE_SECONDS)

    def stop(self) -> None:
        """Signal the run loop to terminate at the next wakeup."""
        self._stop_event.set()
