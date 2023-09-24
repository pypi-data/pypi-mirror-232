from typing import cast

import AppKit
from loguru import logger


def pb2html() -> bytes:
    pb = AppKit.NSPasteboard.generalPasteboard()
    nscfdata = pb.dataForType_(AppKit.NSPasteboardTypeHTML)
    logger.debug(f"capture pasteboard: {nscfdata=}")
    b = cast(bytes, nscfdata.bytes().tobytes())
    with open("b.html", "wb") as f:
        f.write(b)
    logger.debug(f"bytes: {b!r}")
    return b
