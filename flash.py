"""White-LED flash mounted on the Raspberry Pi GPIO."""

import board
import neopixel

_PIXEL_PIN = board.D18
_NUM_PIXELS = 12
_COLOR_ORDER = neopixel.GRB

# Bright white; the flash is only on for the camera shutter window.
_WHITE = (250, 250, 250)
_OFF = (0, 0, 0)


class Flash:
    """Drives a small Neopixel ring used as the camera flash."""

    def __init__(self) -> None:
        self.pixels = neopixel.NeoPixel(
            _PIXEL_PIN, _NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=_COLOR_ORDER
        )

    def on(self) -> None:
        self.pixels.fill(_WHITE)
        self.pixels.show()

    def off(self) -> None:
        self.pixels.fill(_OFF)
        self.pixels.show()

    def disco(self) -> None:
        """Placeholder kept for direct-method API parity with `UVLight.disco`."""
        self.pixels.fill(_OFF)
        self.pixels.show()
