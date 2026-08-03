"""File discovery and natural sorting utilities."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".ts"}
SUBTITLE_EXTENSIONS = {".srt", ".ass", ".vtt", ".sub", ".ssa", ".idx"}


def natural_key(value: str) -> list[object]:
    """Return a case-insensitive key that orders embedded numbers numerically."""
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def _sorted_paths(paths: Iterable[Path]) -> list[Path]:
    """Sort paths naturally by filename, then by parent path for stable results."""
    return sorted(paths, key=lambda p: (natural_key(p.name), natural_key(str(p.parent))))


def scan_media(folder: str | Path, recursive: bool = False) -> tuple[list[Path], list[Path]]:
    """Scan a folder and return naturally sorted video and subtitle paths."""
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"المجلد غير موجود أو غير صالح: {root}")

    candidates = root.rglob("*") if recursive else root.iterdir()
    videos: list[Path] = []
    subtitles: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        suffix = path.suffix.casefold()
        if suffix in VIDEO_EXTENSIONS:
            videos.append(path)
        elif suffix in SUBTITLE_EXTENSIONS:
            subtitles.append(path)

    return _sorted_paths(videos), _sorted_paths(subtitles)
