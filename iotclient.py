"""Azure IoT Hub client wiring direct-method requests to camera + LED actions."""

import logging
import time

from azure.iot.device import IoTHubDeviceClient, MethodResponse

from camera import Camera
from config import (
    ENABLE_INFERENCE,
    IOT_HUB_CONNECTION_STRING,
    STORAGE_ACCOUNT_CONTAINER_NAME,
    STORAGE_ACCOUNT_DIRECTORY_NAME,
    STORAGE_ACCOUNT_NAME,
)
from datalake import DataLake
from flash import Flash
from unattended import Unattended
from utils import create_filename, remove_local_file
from uv import UVLight

logger = logging.getLogger(__name__)


class IotClient:
    """Owns the IoT Hub device client and dispatches direct methods."""

    def __init__(self) -> None:
        self._datalake = DataLake()
        self._flash = Flash()
        self._uv = UVLight()
        self._tensor = None
        if ENABLE_INFERENCE:
            from tensor import Tensor
            self._tensor = Tensor()

        self._unattended_task: Unattended | None = None

        try:
            self._uv.on()
        except Exception:
            logger.exception("Failed to switch UV light on at startup")

        self.client = IoTHubDeviceClient.create_from_connection_string(IOT_HUB_CONNECTION_STRING)

        try:
            self.client.on_method_request_received = self._handle_method_request
        except Exception:
            logger.exception("Failed to attach method handler; shutting client down")
            self.client.shutdown()

    # --- Direct-method dispatch ---

    def _handle_method_request(self, method_request) -> None:
        handlers = {
            "photo": self._do_photo,
            "analyze": self._do_analyze,
            "uv": self._do_uv,
            "flash": self._do_flash,
            "unattended": self._do_unattended,
        }
        handler = handlers.get(method_request.name)
        if handler is None:
            self._respond(method_request, 404, {"Response": "Unknown method"})
            return
        try:
            handler(method_request)
        except Exception:
            logger.exception("Direct method '%s' failed", method_request.name)
            self._respond(method_request, 500, {"Response": "Internal error"})

    def _respond(self, method_request, status: int, payload: dict) -> None:
        response = MethodResponse(method_request.request_id, status, payload)
        self.client.send_method_response(response)

    # --- Method implementations ---

    def _capture_and_upload(self) -> str:
        """Take a picture, upload it to the data lake, return the local filename."""
        camera = Camera()
        filename = create_filename()
        logger.info("Capturing photo: %s", filename)
        self._uv.off()
        self._flash.on()
        try:
            camera.take_picture(filename)
        finally:
            self._flash.off()
            self._uv.on()
        self._datalake.upload_file_to_directory(
            STORAGE_ACCOUNT_CONTAINER_NAME, STORAGE_ACCOUNT_DIRECTORY_NAME, filename
        )
        return filename

    def _do_photo(self, method_request) -> None:
        filename = self._capture_and_upload()
        self._respond(method_request, 200, {"Response": "Photo was taken and uploaded"})
        remove_local_file(filename)

    def _do_analyze(self, method_request) -> None:
        filename = self._capture_and_upload()
        label = self._tensor.process(filename) if self._tensor else "Analysis disabled"
        image_url = "https://{}.blob.core.windows.net/{}/{}/{}".format(
            STORAGE_ACCOUNT_NAME,
            STORAGE_ACCOUNT_CONTAINER_NAME,
            STORAGE_ACCOUNT_DIRECTORY_NAME,
            filename,
        )
        self._respond(method_request, 200, {"ImageUrl": image_url, "Label": label})
        remove_local_file(filename)

    def _do_uv(self, method_request) -> None:
        self._uv.disco()
        self._respond(method_request, 200, {"Response": "UVLight status was changed."})

    def _do_flash(self, method_request) -> None:
        for _ in range(10):
            self._flash.on()
            time.sleep(0.2)
            self._flash.off()
            time.sleep(0.2)
        self._respond(method_request, 200, {"Response": "The moth camera has flashed."})

    def _do_unattended(self, method_request) -> None:
        if self._unattended_task is None:
            self._unattended_task = Unattended()
            self._unattended_task.start()
            self._respond(method_request, 200, {"Response": "Unattended mode started."})
        else:
            self._unattended_task.stop()
            self._unattended_task = None
            self._respond(method_request, 200, {"Response": "Unattended mode stopped."})

    # --- Lifecycle ---

    def shutdown(self) -> None:
        if self._unattended_task is not None:
            self._unattended_task.stop()
        self.client.shutdown()
