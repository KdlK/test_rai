"""Agent-facing wrappers around core dump operations."""

from __future__ import annotations

from typing import Any, Dict, Optional

from renga_api.core.dump import (
    dump_object as core_dump_object,
    dump_selected_object as core_dump_selected_object,
)


def dump_object(com_object: Any) -> Dict[str, Any]:
    """Build a JSON-serializable dump for a Renga COM object.

    :param com_object: COM object to inspect.
    :returns: Structured dump of interfaces, parameters, properties, and geometry.
    """
    return core_dump_object(com_object)


def dump_selected_object() -> Optional[Dict[str, Any]]:
    """Dump the first selected object in the active project.

    :returns: Structured dump or ``None`` when selection is empty.
    """
    return core_dump_selected_object()
