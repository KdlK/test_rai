"""Catalog of agent-facing skill modules."""

from __future__ import annotations

from typing import Iterable

from . import app, dump, model, probe, text


def get_skill_modules() -> Iterable[object]:
    """Return the modules that define the default skill set."""
    return (app, model, text, dump, probe)
