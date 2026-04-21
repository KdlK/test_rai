"""Agent-facing wrappers around core probing operations."""

from __future__ import annotations

from typing import Any, Dict

from renga_api.core.probe import probe_interfaces as core_probe_interfaces


def probe_interfaces(com_object: Any) -> Dict[str, Any]:
    """Probe which COM interfaces are supported by the object.

    :param com_object: COM object to inspect.
    :returns: Supported and unsupported interface summary.
    """
    return core_probe_interfaces(com_object)
