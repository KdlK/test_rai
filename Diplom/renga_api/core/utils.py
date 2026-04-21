"""Small utility helpers shared by the core modules."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def guid_to_str(guid: Any) -> Optional[str]:
    """Convert GUID-like values to a normalized string."""
    if guid is None:
        return None

    if isinstance(guid, str):
        return guid.upper().strip("{}")

    if hasattr(guid, "ToString"):
        return guid.ToString().upper().strip("{}")

    return str(guid).upper().strip("{}")


def save_json(data: Any, path: Path) -> Path:
    """Write JSON data to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def dump_to_file(data: Any, prefix: str = "dump", directory: Optional[Path] = None) -> Path:
    """Save a dump payload under the default dumps directory."""
    target_dir = directory or (Path.cwd() / "dumps")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return save_json(data, target_dir / f"{prefix}_{timestamp}.json")
