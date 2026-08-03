"""Safe preview, batch rename, and undo logic."""
from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class RenameOperation:
    """One requested move from an existing path to a final path."""
    old_path: Path
    new_path: Path
    kind: str
    episode: int


def normalize_season(value: str) -> str:
    """Normalize values such as s2, S02, or season 2 to S02."""
    text = value.strip()
    match = re.fullmatch(r"(?i)(?:s|season\s*)?0*(\d{1,3})", text)
    if not match:
        raise ValueError("أدخل الموسم بصيغة مثل: s2 أو S02 أو season 2")
    number = int(match.group(1))
    if number > 999:
        raise ValueError("رقم الموسم يجب أن يكون بين 0 و999")
    return f"S{number:02d}"


def sanitize_series_name(value: str) -> str:
    """Reject characters that are invalid in common Windows/Linux filenames."""
    name = value.strip().rstrip(". ")
    if any(char in name for char in '<>:"/\\|?*') or "\x00" in name:
        raise ValueError("اسم المسلسل يحتوي على رموز غير مسموحة في أسماء الملفات")
    return name


def build_rename_plan(
    videos: Sequence[str | Path],
    subtitles: Sequence[str | Path],
    season_input: str,
    series_name: str = "",
) -> list[RenameOperation]:
    """Build index-based target names while preserving each original extension/folder."""
    season = normalize_season(season_input)
    series = sanitize_series_name(series_name)
    prefix = f"{series} - " if series else ""
    plan: list[RenameOperation] = []

    total = max(len(videos), len(subtitles))
    for index in range(total):
        stem = f"{prefix}{season}E{index + 1:02d}"
        if index < len(videos):
            old = Path(videos[index]).resolve()
            plan.append(RenameOperation(old, old.with_name(stem + old.suffix), "فيديو", index + 1))
        if index < len(subtitles):
            old = Path(subtitles[index]).resolve()
            plan.append(RenameOperation(old, old.with_name(stem + old.suffix), "ترجمة", index + 1))

    validate_plan(plan)
    return plan


def validate_plan(plan: Sequence[RenameOperation]) -> None:
    """Validate source existence, duplicate targets, and external collisions."""
    sources = {op.old_path for op in plan}
    targets: set[Path] = set()
    for op in plan:
        if not op.old_path.is_file():
            raise FileNotFoundError(f"الملف غير موجود: {op.old_path}")
        if op.new_path in targets:
            raise FileExistsError(f"أكثر من ملف سيحصل على الاسم نفسه: {op.new_path}")
        targets.add(op.new_path)
        if op.new_path.exists() and op.new_path not in sources and op.new_path != op.old_path:
            raise FileExistsError(f"الاسم مستخدم مسبقًا: {op.new_path}")


def execute_rename(plan: Sequence[RenameOperation]) -> list[tuple[Path, Path]]:
    """Rename transactionally through temporary names; roll back on any error."""
    validate_plan(plan)
    changed = [op for op in plan if op.old_path != op.new_path]
    if not changed:
        return []

    staged: list[tuple[Path, Path, Path]] = []  # old, temp, final
    finalized: list[tuple[Path, Path]] = []
    try:
        for op in changed:
            temp = op.old_path.with_name(f".{op.old_path.name}.jbr-{uuid.uuid4().hex}.tmp")
            os.rename(op.old_path, temp)
            staged.append((op.old_path, temp, op.new_path))

        for old, temp, final in staged:
            os.rename(temp, final)
            finalized.append((old, final))
        return finalized
    except Exception as exc:
        # Restore finalized and still-staged files in reverse order where possible.
        for old, final in reversed(finalized):
            try:
                if final.exists() and not old.exists():
                    os.rename(final, old)
            except OSError:
                pass
        for old, temp, _final in reversed(staged):
            try:
                if temp.exists() and not old.exists():
                    os.rename(temp, old)
            except OSError:
                pass
        raise OSError(f"تعذرت عملية إعادة التسمية: {exc}") from exc


def undo_rename(history: Sequence[tuple[Path, Path]]) -> None:
    """Undo the most recent successful batch using the same transactional engine."""
    reverse_plan = [RenameOperation(new, old, "تراجع", index + 1) for index, (old, new) in enumerate(history)]
    execute_rename(reverse_plan)
