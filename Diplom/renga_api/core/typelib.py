"""Type library helpers for Renga COM interfaces."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import comtypes.client
from comtypes import automation, typeinfo

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_TLB_PATHS = (
    PACKAGE_ROOT / "tlb" / "RengaCOMAPI.tlb",
    Path(r"C:\Program Files\Renga Professional\RengaCOMAPI.tlb"),
    Path(r"C:\Program Files\Renga Standard\RengaCOMAPI.tlb"),
    Path(r"C:\Program Files\Renga Professional\RengaCOMAPI.dll"),
)

PARAMFLAG_FIN = 0x1
PARAMFLAG_FOUT = 0x2

VT_KIND_NAMES = {
    automation.VT_BOOL: "bool",
    automation.VT_BSTR: "string",
    automation.VT_DISPATCH: "dispatch",
    automation.VT_I4: "int",
    automation.VT_PTR: "pointer",
    automation.VT_R8: "double",
    automation.VT_SAFEARRAY: "safearray",
    automation.VT_UNKNOWN: "unknown",
    automation.VT_USERDEFINED: "userdefined",
    automation.VT_VOID: "void",
}
TYPE_KIND_NAMES = {
    typeinfo.TKIND_ALIAS: "alias",
    typeinfo.TKIND_COCLASS: "coclass",
    typeinfo.TKIND_DISPATCH: "dispatch",
    typeinfo.TKIND_ENUM: "enum",
    typeinfo.TKIND_INTERFACE: "interface",
    typeinfo.TKIND_MODULE: "module",
    typeinfo.TKIND_RECORD: "record",
    typeinfo.TKIND_UNION: "union",
}
INVOKE_KIND_NAMES = {
    automation.INVOKE_FUNC: "method",
    automation.INVOKE_PROPERTYGET: "property_get",
    automation.INVOKE_PROPERTYPUT: "property_put",
    automation.INVOKE_PROPERTYPUTREF: "property_putref",
}

_typelib: Optional[Any] = None
_typelib_path: Optional[Path] = None
_registry: Optional[Dict[str, Dict[str, Any]]] = None
_registry_path: Optional[Path] = None
_metadata_registry: Optional[Dict[str, Dict[str, Any]]] = None
_metadata_registry_path: Optional[Path] = None


def _resolve_tlb_path(tlb_path: Optional[Path] = None) -> Path:
    """Resolve the path to ``RengaCOMAPI.tlb``."""
    if tlb_path is not None:
        path = Path(tlb_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"Type library not found: {path}")

    env_path = os.environ.get("RENGA_TLB_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    for path in DEFAULT_TLB_PATHS:
        if path.exists():
            return path

    raise FileNotFoundError(
        "RengaCOMAPI.tlb not found. Set RENGA_TLB_PATH or place it in renga_ai/tlb."
    )


def get_typelib(tlb_path: Optional[Path] = None) -> Any:
    """Load and cache the Renga type library."""
    global _typelib, _typelib_path

    resolved_path = _resolve_tlb_path(tlb_path)
    if _typelib is not None and _typelib_path == resolved_path:
        return _typelib

    _typelib = typeinfo.LoadTypeLibEx(str(resolved_path))
    _typelib_path = resolved_path
    return _typelib


def get_interface_registry(tlb_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Return a registry of generated COM interface types keyed by name."""
    global _registry, _registry_path

    resolved_path = _resolve_tlb_path(tlb_path)
    if _registry is not None and _registry_path == resolved_path:
        return _registry

    typelib = get_typelib(resolved_path)
    comtypes.client.GetModule(str(resolved_path))
    from comtypes.gen import Renga

    registry: Dict[str, Dict[str, Any]] = {}
    for index in range(typelib.GetTypeInfoCount()):
        name = typelib.GetDocumentation(index)[0]
        if not name.startswith("I"):
            continue

        iface_type = getattr(Renga, name, None)
        if iface_type is None:
            continue

        iid = getattr(iface_type, "_iid_", None)
        if iid is None:
            continue

        registry[name] = {
            "guid": str(iid),
            "index": index,
            "name": name,
            "type": iface_type,
        }

    _registry = registry
    _registry_path = resolved_path
    return _registry


def get_interface_type(name: str) -> Optional[Any]:
    """Return the generated interface type by name."""
    info = get_interface_registry().get(name)
    return info["type"] if info else None


def get_interface_guid(name: str) -> Optional[str]:
    """Return the interface GUID string by name."""
    info = get_interface_registry().get(name)
    return info["guid"] if info else None


def get_interface_metadata_registry(
    tlb_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """Return TLB-derived metadata for COM interfaces keyed by name."""
    global _metadata_registry, _metadata_registry_path

    resolved_path = _resolve_tlb_path(tlb_path)
    if _metadata_registry is not None and _metadata_registry_path == resolved_path:
        return _metadata_registry

    typelib = get_typelib(resolved_path)
    registry = get_interface_registry(resolved_path)
    metadata_registry: Dict[str, Dict[str, Any]] = {}

    for name, info in registry.items():
        type_info = typelib.GetTypeInfo(info["index"])
        type_attr = type_info.GetTypeAttr()
        members = []

        for func_index in range(type_attr.cFuncs):
            func_desc = type_info.GetFuncDesc(func_index)
            names = type_info.GetNames(func_desc.memid, func_desc.cParams + 1)
            member_name = names[0]
            parameters = []
            input_param_count = 0
            output_param_count = 0

            for param_index in range(func_desc.cParams):
                param_desc = func_desc.lprgelemdescParam[param_index]
                param_flags = int(param_desc._.paramdesc.wParamFlags)
                is_input = param_flags == 0 or bool(param_flags & PARAMFLAG_FIN)
                is_output = bool(param_flags & PARAMFLAG_FOUT)
                if is_input:
                    input_param_count += 1
                if is_output:
                    output_param_count += 1

                parameters.append(
                    {
                        "is_input": is_input,
                        "is_output": is_output,
                        "name": (
                            names[param_index + 1]
                            if param_index + 1 < len(names)
                            else f"param_{param_index}"
                        ),
                        "type": _describe_typedesc(type_info, param_desc.tdesc),
                    }
                )

            members.append(
                {
                    "input_param_count": input_param_count,
                    "invoke_kind": int(func_desc.invkind),
                    "invoke_kind_name": INVOKE_KIND_NAMES.get(
                        int(func_desc.invkind),
                        f"invoke_{int(func_desc.invkind)}",
                    ),
                    "member_id": int(func_desc.memid),
                    "name": member_name,
                    "output_param_count": output_param_count,
                    "param_count": int(func_desc.cParams),
                    "params": parameters,
                    "return_type": _describe_typedesc(type_info, func_desc.elemdescFunc.tdesc),
                }
            )

        metadata_registry[name] = {
            "guid": info["guid"],
            "index": info["index"],
            "members": members,
            "name": name,
        }

    _metadata_registry = metadata_registry
    _metadata_registry_path = resolved_path
    return _metadata_registry


def get_interface_metadata(name: str) -> Optional[Dict[str, Any]]:
    """Return TLB-derived metadata for a COM interface by name."""
    return get_interface_metadata_registry().get(name)


def get_interface_members(name: str) -> list[Dict[str, Any]]:
    """Return TLB-derived member metadata for a COM interface."""
    metadata = get_interface_metadata(name)
    if metadata is None:
        return []
    return metadata["members"]


def _describe_typedesc(owner_type_info: Any, typedesc: Any) -> Dict[str, Any]:
    vt = int(typedesc.vt)
    description: Dict[str, Any] = {
        "kind": VT_KIND_NAMES.get(vt, "primitive"),
        "vt": vt,
    }

    if vt == automation.VT_PTR:
        target = _describe_typedesc(owner_type_info, typedesc._.lptdesc[0])
        description["name"] = target.get("name")
        description["target"] = target
        description["typekind"] = target.get("typekind")
        return description

    if vt == automation.VT_USERDEFINED:
        ref_type_info = owner_type_info.GetRefTypeInfo(typedesc._.hreftype)
        ref_type_attr = ref_type_info.GetTypeAttr()
        description["kind"] = TYPE_KIND_NAMES.get(
            int(ref_type_attr.typekind),
            f"typekind_{int(ref_type_attr.typekind)}",
        )
        description["name"] = ref_type_info.GetDocumentation(-1)[0]
        description["typekind"] = int(ref_type_attr.typekind)
        return description

    return description
