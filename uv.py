"""UV LED panel that attracts moths to the camera."""

import logging
import time

import board
import neopixel

logger = logging.getLogger(__name__)

_PIXEL_PIN = board.D21
_NUM_PIXELS = 60
_COLOR_ORDER = neopixel.RGB

# Approximate "blacklight" tint; UV-tuned LEDs differ in colour balance.
_UV_COLOR = (148, 6, 62)
_OFF = (0, 0, 0)

_DISCO_DURATION_SECONDS = 10


class UVLight:
    """Drives the 60-pixel UV Neopixel panel."""

    def __init__(self) -> None:
        self.pixels = neopixel.NeoPixel(
            _PIXEL_PIN, _NUM_PIXELS, brightness=0.4, auto_write=False, pixel_order=_COLOR_ORDER
        )

    def on(self) -> None:
        self.pixels.fill(_UV_COLOR)
        self.pixels.show()

    def off(self) -> None:
        self.pixels.fill(_OFF)
        self.pixels.show()

    def disco(self) -> None:
        """Run a rainbow cycle for a few seconds, then return to UV."""
        start_time = time.time()
        while (time.time() - start_time) < _DISCO_DURATION_SECONDS:
            self._rainbow_cycle(0)
        self.pixels.fill(_UV_COLOR)
        self.pixels.show()

    def _wheel(self, pos: int) -> tuple:
        """Map 0..255 -> a colour around the colour wheel."""
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r, g, b = int(pos * 3), int(255 - pos * 3), 0
        elif pos < 170:
            pos -= 85
            r, g, b = int(255 - pos * 3), 0, int(pos * 3)
        else:
            pos -= 170
            r, g, b = 0, int(pos * 3), int(255 - pos * 3)
        if _COLOR_ORDER in (neopixel.RGB, neopixel.GRB):
            return (r, g, b)
        return (r, g, b, 0)

    def _rainbow_cycle(self, wait: float) -> None:
        for j in range(255):
            for i in range(_NUM_PIXELS):
                self.pixels[i] = self._wheel(((i * 256 // _NUM_PIXELS) + j) & 255)
            self.pixels.show()
            if wait:
                time.sleep(wait)
