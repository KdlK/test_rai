"""Safe helpers for probing Renga COM objects."""

from __future__ import annotations

from typing import Any, Dict, Optional

import comtypes

from .typelib import get_interface_registry, get_interface_type


def probe_interfaces(com_object: Any) -> Dict[str, Any]:
    """Return supported and unsupported interfaces for a COM object."""
    supported = []
    unsupported = []

    for name, info in get_interface_registry().items():
        try:
            com_object.QueryInterface(info["type"])
            supported.append({"guid": info["guid"], "name": name})
        except (comtypes.COMError, OSError):
            unsupported.append(name)

    return {
        "supported": supported,
        "supported_count": len(supported),
        "supported_names": [item["name"] for item in supported],
        "unsupported": unsupported,
        "unsupported_count": len(unsupported),
    }


def get_interface(com_object: Any, name: str) -> Optional[Any]:
    """Return a specific interface from a COM object."""
    iface_type = get_interface_type(name)
    if iface_type is not None:
        try:
            return com_object.QueryInterface(iface_type)
        except (comtypes.COMError, OSError):
            pass

    return call_method_safe(com_object, "GetInterfaceByName", name)


def has_interface(com_object: Any, name: str) -> bool:
    """Return ``True`` when the object supports the requested interface."""
    return get_interface(com_object, name) is not None


def get_property_safe(obj: Any, name: str) -> Any:
    """Read an attribute and return ``None`` on COM-related failures."""
    try:
        return getattr(obj, name)
    except (AttributeError, comtypes.COMError, OSError):
        return None


def call_method_safe(obj: Any, name: str, *args: Any, **kwargs: Any) -> Any:
    """Call an object method and return ``None`` on COM-related failures."""
    try:
        method = getattr(obj, name)
        return method(*args, **kwargs)
    except (AttributeError, TypeError, comtypes.COMError, OSError):
        return None
