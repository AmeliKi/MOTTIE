#!/usr/bin/env python3
"""Smoke test for the OAK-1 camera integration.

Run on the Raspberry Pi with the OAK-1 attached:
    python3 test_oak1_camera.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera import Camera


def test_camera() -> bool:
    """Initialise the camera, capture one frame, and verify the file exists."""
    print("Testing OAK-1 camera integration...")

    try:
        print("1. Initializing camera...")
        camera = Camera()
        print("   Camera initialized successfully")

        print("2. Reading image configuration...")
        print(f"   Image config: {camera.get_image_config()}")

        print("3. Taking test picture...")
        test_filename = "test_oak1_image.jpg"
        camera.take_picture(test_filename)

        if not os.path.exists(test_filename):
            print("   Failed to create image file")
            return False

        print(f"   Image captured: {test_filename} ({os.path.getsize(test_filename)} bytes)")
        print("\nAll tests passed - OAK-1 camera is working.")
        return True

    except Exception as e:
        print(f"   Error during testing: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if test_camera() else 1)
