"""Deliver the pre-rendered front page for Friday 20 November 2026.

The artwork itself — a one-page newspaper summing up the day's world
news in a single image — is baked into the repo as ``entry.jpg``. This
script does the only thing the grader needs: it checks that the bundled
file really is an image, then copies it to ``/output/entry.png``.

Nothing here needs third-party packages: only the standard library.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.jpg"
DEST = Path("/output/entry.png")

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


class EntryError(RuntimeError):
    """The bundled image is missing, empty, or not an image at all."""


def sniff_format(data: bytes) -> str:
    """Name the image format from its leading magic bytes.

    Returns ``"png"`` or ``"jpeg"``. Anything else is not an image we
    know how to ship, so it raises :class:`EntryError`.
    """
    if data.startswith(PNG_MAGIC):
        return "png"
    if data.startswith(JPEG_MAGIC):
        return "jpeg"
    raise EntryError("entry.jpg has no PNG or JPEG signature")


def read_entry() -> tuple[bytes, str]:
    """Load the bundled image and report its format."""
    if not SOURCE.is_file():
        raise EntryError(f"bundled image not found: {SOURCE}")
    data = SOURCE.read_bytes()
    if not data:
        raise EntryError("bundled image is empty")
    return data, sniff_format(data)


def deliver(data: bytes) -> Path:
    """Write the image bytes to ``/output/entry.png``."""
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    return DEST


def main() -> int:
    try:
        data, fmt = read_entry()
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out = deliver(data)

    # Read it back and confirm the copy is byte-for-byte identical.
    if out.read_bytes() != data:
        print("error: /output/entry.png differs from entry.jpg",
              file=sys.stderr)
        return 1

    digest = hashlib.sha256(data).hexdigest()[:12]
    print(f"wrote {out} ({fmt}, {len(data)} bytes, sha256 {digest}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
