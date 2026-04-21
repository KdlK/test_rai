"""Discovery helpers for the default Renga skill set."""

from __future__ import annotations

import inspect
from typing import Any

from .catalog import get_skill_modules


def get_skills_catalog() -> list[dict[str, Any]]:
    """Return skill metadata with function name, module, and documentation."""
    skills: list[dict[str, Any]] = []

    for module in get_skill_modules():
        for name in dir(module):
            if name.startswith("_"):
                continue

            obj = getattr(module, name)
            if not inspect.isfunction(obj):
                continue
            if obj.__module__ != module.__name__:
                continue

            skills.append(
                {
                    "description": inspect.getdoc(obj) or "",
                    "module": module.__name__,
                    "name": obj.__name__,
                }
            )

    return sorted(skills, key=lambda item: (item["module"], item["name"]))
