"""OAK-1 (DepthAI) RGB camera wrapper."""

import logging
import time

import cv2
import depthai as dai

from config import IMAGE_FORMAT, IMAGE_HEIGHT, IMAGE_WIDTH

logger = logging.getLogger(__name__)

_LENS_FOCUS = 120  # Manual focus position (0..255); tuned for the moth setup.


class Camera:
    """OAK-1 single-frame capture pipeline."""

    def __init__(self) -> None:
        self.image_width = IMAGE_WIDTH
        self.image_height = IMAGE_HEIGHT
        self.image_format = IMAGE_FORMAT
        self.pipeline = self._build_pipeline()

    def _build_pipeline(self) -> dai.Pipeline:
        pipeline = dai.Pipeline()
        cam_rgb = pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(self.image_width, self.image_height)
        cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
        cam_rgb.setInterleaved(False)
        cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        cam_rgb.initialControl.setManualFocus(_LENS_FOCUS)

        xout = pipeline.create(dai.node.XLinkOut)
        xout.setStreamName("rgb")
        cam_rgb.preview.link(xout.input)
        return pipeline

    def take_picture(self, filename: str) -> None:
        """Capture a single frame and write it to `filename`."""
        try:
            with dai.Device(self.pipeline) as device:
                queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
                # Allow auto-exposure / focus to settle before grabbing the frame.
                time.sleep(1)
                in_rgb = queue.get()
                frame = in_rgb.getCvFrame()
                cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        except Exception:
            logger.exception("Camera capture failed for %s", filename)

    def get_image_config(self) -> dict:
        return {"width": self.image_width, "height": self.image_height, "format": self.image_format}

    def set_image_config(self, image_width: int, image_height: int, image_format: str) -> None:
        """Reconfigure capture dimensions; rebuilds the pipeline."""
        self.image_width = image_width
        self.image_height = image_height
        self.image_format = image_format
        self.pipeline = self._build_pipeline()
