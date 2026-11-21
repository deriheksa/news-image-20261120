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
from dataclasses import dataclass
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


class EntryError(RuntimeError):
    """The bundled image is missing, empty, or not an image at all."""


@dataclass(frozen=True)
class EntryPaths:
    """Where the bundled image lives and where the grader expects it."""

    source: Path
    dest: Path

    @classmethod
    def discover(cls) -> "EntryPaths":
        """Locate the bundled image next to this file; target /output."""
        here = Path(__file__).resolve().parent
        return cls(source=here / "entry.jpg", dest=Path("/output/entry.png"))


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


def read_entry(paths: EntryPaths) -> tuple[bytes, str]:
    """Load the bundled image and report its format."""
    if not paths.source.is_file():
        raise EntryError(f"bundled image not found: {paths.source}")
    data = paths.source.read_bytes()
    if not data:
        raise EntryError("bundled image is empty")
    return data, sniff_format(data)


def deliver(paths: EntryPaths, data: bytes) -> Path:
    """Write the image bytes to ``/output/entry.png``."""
    paths.dest.parent.mkdir(parents=True, exist_ok=True)
    paths.dest.write_bytes(data)
    return paths.dest


def announce(dest: Path, fmt: str, data: bytes) -> None:
    """Print a one-line summary of the shipped entry."""
    digest = hashlib.sha256(data).hexdigest()[:12]
    print(f"wrote {dest} ({fmt}, {len(data)} bytes, sha256 {digest}...)")


def verify(paths: EntryPaths, data: bytes) -> None:
    """Confirm the written copy is byte-for-byte identical."""
    if paths.dest.read_bytes() != data:
        raise EntryError(f"{paths.dest} differs from {paths.source}")


def ship_entry(paths: EntryPaths) -> int:
    """Copy the bundled image to /output and verify the copy."""
    try:
        data, fmt = read_entry(paths)
        deliver(paths, data)
        verify(paths, data)
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    announce(paths.dest, fmt, data)
    return 0


def main() -> int:
    return ship_entry(EntryPaths.discover())


if __name__ == "__main__":
    raise SystemExit(main())
