# -*- coding: utf-8 -*-
#
# ███╗   ███╗    ██████╗ ████████╗████████╗██╗   ███████╗
# ████╗ ████║   ██╔═══██╗╚══██╔══╝╚══██╔══╝██║   ██╔════╝
# ██╔████╔██║   ██║   ██║   ██║      ██║   ██║   █████╗
# ██║╚██╔╝██║   ██║   ██║   ██║      ██║   ██║   ██╔══╝
# ██║ ╚═╝ ██║██╗╚██████╔╝██╗██║██╗   ██║██╗██║██╗███████╗██╗
# ╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝╚═╝╚═╝   ╚═╝╚═╝╚═╝╚═╝╚══════╝╚═╝
#
# Moth Optical Tracking and Taxonomic Identification Equipment
#
# Copyright (c) Dr. Ameli Kirse (LIB), Tillmann Eitelberg (oh22).
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""MOTTIE entry point.

Boots the IoT Hub client (when enabled) and starts the unattended capture
thread. The IoT-Hub client owns the direct-method dispatcher; the unattended
thread runs in parallel and can also be started/stopped via the `unattended`
direct method.
"""

import datetime
import logging
import os
import time

from config import ENABLE_IOT
from unattended import Unattended

logger = logging.getLogger(__name__)

# Time-of-day after which a long-running session shuts down (overnight runs).
_SHUTDOWN_AFTER = datetime.time(23, 15)


def _print_banner() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print("")
    print("███╗   ███╗    ██████╗ ████████╗████████╗██╗   ███████╗")
    print("████╗ ████║   ██╔═══██╗╚══██╔══╝╚══██╔══╝██║   ██╔════╝")
    print("██╔████╔██║   ██║   ██║   ██║      ██║   ██║   █████╗")
    print("██║╚██╔╝██║   ██║   ██║   ██║      ██║   ██║   ██╔══╝")
    print("██║ ╚═╝ ██║██╗╚██████╔╝██╗██║██╗   ██║██╗██║██╗███████╗██╗")
    print("╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝╚═╝╚═╝   ╚═╝╚═╝╚═╝╚═╝╚══════╝╚═╝")
    print("")
    print("Moth Optical Tracking and Taxonomic Identification Equipment")
    print("")
    print("Copyright (c) Dr. Ameli Kirse (LIB), Tillmann Eitelberg (oh22).")
    print("Licensed under the MIT license. See LICENSE file in the project root for full license information.")
    print("")
    print("You can send the following Device Direct Methods to the MothCam:")
    print("")
    print("═> photo")
    print("═> analyze")
    print("═> uv")
    print("═> flash")
    print("═> unattended")
    print("")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    _print_banner()
    print("Current working directory:", os.getcwd())

    iot_client = None
    if ENABLE_IOT:
        from iotclient import IotClient
        iot_client = IotClient()

    print("Starting unattended mode automatically...")
    task_thread = Unattended()
    task_thread.start()
    print("Unattended mode started - taking photos every 5 minutes")

    try:
        while True:
            time.sleep(60)
            if datetime.datetime.now().time() > _SHUTDOWN_AFTER:
                logger.info("Past shutdown time; exiting main loop")
                break
    except KeyboardInterrupt:
        print("MOTTIE interrupted by user")
    finally:
        print("Shutting down")
        task_thread.stop()
        task_thread.join(timeout=5)
        if iot_client is not None:
            iot_client.shutdown()


if __name__ == "__main__":
    main()
