"""Serialization helpers for Renga COM objects."""

from __future__ import annotations

from typing import Any, Dict, Optional

import comtypes

from .app import get_model, get_project, get_selection
from .probe import call_method_safe, get_interface, get_property_safe, probe_interfaces
from .typelib import get_interface_members

SAFE_METHOD_PREFIXES = ("Can", "Calculate", "Find", "Get", "Has", "Is")
GENERIC_METHOD_NAMES = {
    "AddRef",
    "from_param",
    "GetIDsOfNames",
    "GetTypeInfo",
    "GetTypeInfoCount",
    "Invoke",
    "QueryInterface",
    "Release",
}
GENERIC_PROPERTY_NAMES = {"value"}
MAX_COLLECTION_ITEMS = 50
MAX_DEPTH = 3
GEOMETRY_TYPE_TOKENS = (
    "2D",
    "3D",
    "Contour",
    "Curve",
    "Grid",
    "Mesh",
    "Placement",
    "Point",
    "Transform",
    "Triangle",
    "Vector",
)

PARAMETER_GETTERS = {
    1: ("GetBoolValue",),
    2: ("GetIntValue",),
    3: ("GetDoubleValue",),
    4: ("GetStringValue",),
}
PROPERTY_GETTERS = {
    1: ("GetDoubleValue",),
    2: ("GetStringValue",),
    3: ("GetAngleValue", "GetDoubleValue"),
    4: ("GetAreaValue", "GetDoubleValue"),
    5: ("GetBooleanValue",),
    6: ("GetEnumerationValue", "GetIntegerValue"),
    7: ("GetIntegerValue",),
    8: ("GetLengthValue", "GetDoubleValue"),
    9: ("GetLogicalValue", "GetBooleanValue"),
    10: ("GetMassValue", "GetDoubleValue"),
    11: ("GetVolumeValue", "GetDoubleValue"),
}
FALLBACK_GETTERS = (
    "GetStringValue",
    "GetBooleanValue",
    "GetBoolValue",
    "GetIntegerValue",
    "GetIntValue",
    "GetDoubleValue",
)


def dump_object(com_object: Any) -> Dict[str, Any]:
    """Build a JSON-serializable dump of a Renga object."""
    base = {
        "id": get_property_safe(com_object, "Id"),
        "name": get_property_safe(com_object, "Name"),
        "type_id": get_property_safe(com_object, "ObjectTypeS"),
        "unique_id": get_property_safe(com_object, "UniqueIdS"),
    }

    probe_result = probe_interfaces(com_object)
    interfaces = []
    for iface_info in probe_result["supported"]:
        iface_object = get_interface(com_object, iface_info["name"])
        if iface_object is None:
            continue

        interfaces.append(
            {
                "guid": iface_info["guid"],
                "name": iface_info["name"],
                **_dump_interface(iface_object),
            }
        )

    parameters = _dump_parameter_container(call_method_safe(com_object, "GetParameters"))
    properties = _dump_property_container(call_method_safe(com_object, "GetProperties"))

    return {
        **base,
        "geometry": _dump_geometry(com_object, probe_result),
        "interface_summary": {
            "supported_count": probe_result["supported_count"],
            "supported_names": probe_result["supported_names"],
            "unsupported_count": probe_result["unsupported_count"],
        },
        "interfaces": interfaces,
        "parameters": parameters,
        "properties": properties,
    }


def dump_selected_object() -> Optional[Dict[str, Any]]:
    """Dump the first selected object in the active project."""
    selected_id = _get_first_selected_id()
    if selected_id is None:
        return None

    obj = get_model().GetObjects().GetById(selected_id)
    return dump_object(obj)


def _get_first_selected_id() -> Optional[int]:
    selected = call_method_safe(get_selection(), "GetSelectedObjects")
    if selected is None:
        return None

    count = get_property_safe(selected, "Count")
    if count is not None:
        if int(count) <= 0:
            return None
        return call_method_safe(selected, "Get", 0)

    try:
        if len(selected) == 0:
            return None
        return selected[0]
    except TypeError:
        return None


def _dump_interface(iface_object: Any) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}
    methods: Dict[str, Any] = {}
    available_methods = []
    skipped_methods = []

    for attr in dir(iface_object):
        if attr.startswith("_"):
            continue

        try:
            value = getattr(iface_object, attr)
        except Exception:
            continue

        if callable(value):
            if attr in GENERIC_METHOD_NAMES:
                continue

            available_methods.append(attr)
            if attr.startswith(SAFE_METHOD_PREFIXES):
                result = call_method_safe(iface_object, attr)
                if result is not None:
                    methods[attr] = _serialize_value(result)
                else:
                    skipped_methods.append(attr)
            else:
                skipped_methods.append(attr)
            continue

        if attr in GENERIC_PROPERTY_NAMES:
            continue
        properties[attr] = _serialize_value(value)

    return {
        "available_methods": sorted(available_methods),
        "methods": methods,
        "properties": properties,
        "skipped_methods": sorted(skipped_methods),
    }


def _dump_parameter_container(container: Any) -> list[Dict[str, Any]]:
    if container is None:
        return []

    result = []
    ids = call_method_safe(container, "GetIds")
    count = get_property_safe(ids, "Count")
    if ids is None or count is None:
        return result

    for index in range(int(count)):
        param_id = call_method_safe(ids, "Get", index)
        param = call_method_safe(container, "Get", param_id)
        if param is None:
            continue

        definition = get_property_safe(param, "Definition")
        entry = {
            "group_text": get_property_safe(definition, "GroupText"),
            "has_value": get_property_safe(param, "HasValue"),
            "id": get_property_safe(param, "IdS"),
            "is_read_only": get_property_safe(param, "IsReadOnly"),
            "name": get_property_safe(definition, "Name"),
            "parameter_type": get_property_safe(definition, "ParameterType"),
            "text": get_property_safe(definition, "Text"),
            "value": None,
            "value_type": get_property_safe(param, "ValueType"),
        }

        if entry["has_value"]:
            entry["value"] = _read_parameter_value(param, entry["value_type"])

        result.append(entry)

    return result


def _dump_property_container(container: Any) -> list[Dict[str, Any]]:
    if container is None:
        return []

    result = []
    ids = call_method_safe(container, "GetIds")
    count = get_property_safe(ids, "Count")
    if ids is None or count is None:
        return result

    for index in range(int(count)):
        prop_id = call_method_safe(ids, "Get", index)
        prop = call_method_safe(container, "Get", prop_id)
        if prop is None:
            continue

        entry = {
            "id": get_property_safe(prop, "IdS"),
            "name": get_property_safe(prop, "Name"),
            "type": get_property_safe(prop, "Type"),
            "value": _read_property_value(prop, get_property_safe(prop, "Type")),
        }
        result.append(entry)

    return result


def _read_parameter_value(param: Any, value_type: Any) -> Any:
    getter_names = PARAMETER_GETTERS.get(value_type, FALLBACK_GETTERS)
    return _read_first_supported_value(param, getter_names)


def _read_property_value(prop: Any, property_type: Any) -> Any:
    getter_names = PROPERTY_GETTERS.get(property_type, FALLBACK_GETTERS)
    return _read_first_supported_value(prop, getter_names)


def _read_first_supported_value(obj: Any, getter_names: tuple[str, ...]) -> Any:
    seen = set()
    for getter_name in getter_names:
        if getter_name in seen:
            continue
        seen.add(getter_name)

        value = call_method_safe(obj, getter_name)
        if value is not None:
            return value

    return None


def _dump_geometry(com_object: Any, probe_result: Dict[str, Any]) -> Dict[str, Any]:
    geometry_interfaces: Dict[str, Any] = {}
    for iface_info in probe_result["supported"]:
        iface_name = iface_info["name"]
        if not _interface_has_geometry_data(iface_name):
            continue

        iface_object = get_interface(com_object, iface_name)
        if iface_object is None:
            continue

        dumped = _dump_tlb_interface(iface_object, iface_name, depth=0, visited=set())
        if dumped:
            geometry_interfaces[iface_name] = dumped

    geometry: Dict[str, Any] = {}
    if geometry_interfaces:
        geometry["interfaces"] = geometry_interfaces

    exported_3d = _dump_exported_object_geometry(get_property_safe(com_object, "Id"))
    if exported_3d is not None:
        geometry["exported_3d"] = exported_3d

    return geometry


def _dump_exported_object_geometry(object_id: Any) -> Optional[Dict[str, Any]]:
    if object_id is None:
        return None

    project = get_project()
    if project is None:
        return None

    exporter = get_property_safe(project, "DataExporter")
    if exporter is None:
        return None

    objects3d = call_method_safe(exporter, "GetObjects3D")
    if objects3d is None:
        return None

    collection_members = get_interface_members("IExportedObject3DCollection")
    get_member = next(
        (
            member
            for member in collection_members
            if member["name"] == "Get" and member["input_param_count"] == 1
        ),
        None,
    )
    count = get_property_safe(objects3d, "Count")
    if get_member is None or count is None:
        return None

    for index in range(int(count)):
        exported_object = call_method_safe(objects3d, "Get", index)
        if exported_object is None:
            continue
        if get_property_safe(exported_object, "ModelObjectId") != object_id:
            continue

        serialized = _serialize_tlb_value(
            exported_object,
            get_member["return_type"],
            depth=0,
            visited=set(),
        )
        if isinstance(serialized, dict):
            return serialized
        return {"value": serialized}

    return None


def _dump_tlb_interface(
    iface_object: Any,
    interface_name: str,
    depth: int,
    visited: set[tuple[str, int]],
) -> Any:
    if depth >= MAX_DEPTH:
        return _serialize_value(iface_object, depth)

    members = get_interface_members(interface_name)
    if not members:
        return _serialize_value(iface_object, depth)

    if _is_collection_interface(interface_name):
        return _dump_tlb_collection(iface_object, interface_name, depth, visited)

    interface_is_geometry = _interface_is_geometry_like(interface_name)
    dumped: Dict[str, Any] = {}

    for member in members:
        if not _should_dump_member(interface_name, member, interface_is_geometry):
            continue

        result = _call_tlb_member(iface_object, member)
        if result is None:
            continue

        dumped[member["name"]] = _serialize_member_result(result, member, depth, visited)

    for member in members:
        if not _should_dump_indexed_member(member, dumped):
            continue

        count = _get_indexed_member_count(iface_object, members, member)
        if count is None:
            continue

        dumped[member["name"]] = _dump_indexed_member_items(
            iface_object,
            member,
            count,
            depth,
            visited,
        )

    return dumped


def _dump_tlb_collection(
    collection_object: Any,
    interface_name: str,
    depth: int,
    visited: set[tuple[str, int]],
) -> Dict[str, Any]:
    members = get_interface_members(interface_name)
    count = int(get_property_safe(collection_object, "Count") or 0)
    get_member = next(
        (
            member
            for member in members
            if member["name"] == "Get" and member["input_param_count"] == 1
        ),
        None,
    )
    if get_member is None:
        return {"count": count, "items": [], "truncated": False}

    items = []
    limit = min(count, MAX_COLLECTION_ITEMS)
    for index in range(limit):
        item = call_method_safe(collection_object, "Get", index)
        items.append(
            _serialize_tlb_value(
                item,
                get_member["return_type"],
                depth + 1,
                visited,
            )
        )

    return {
        "count": count,
        "items": items,
        "truncated": count > limit,
    }


def _should_dump_member(
    interface_name: str,
    member: Dict[str, Any],
    interface_is_geometry: bool,
) -> bool:
    if member["name"] in GENERIC_METHOD_NAMES:
        return False
    if member["invoke_kind_name"] not in {"method", "property_get"}:
        return False
    if member["input_param_count"] != 0:
        return False

    return_type_name = _get_type_name(member["return_type"])
    if return_type_name == interface_name and member["name"].startswith("Get"):
        return False

    if interface_is_geometry:
        return True

    return _type_is_geometry(member["return_type"])


def _call_tlb_member(iface_object: Any, member: Dict[str, Any]) -> Any:
    if member["invoke_kind_name"] == "property_get":
        return get_property_safe(iface_object, member["name"])
    return call_method_safe(iface_object, member["name"])


def _serialize_member_result(
    value: Any,
    member: Dict[str, Any],
    depth: int,
    visited: set[tuple[str, int]],
) -> Any:
    if member["return_type"]["kind"] == "void" and member["output_param_count"] > 0:
        output_values = value if isinstance(value, (list, tuple)) else [value]
        serialized: Dict[str, Any] = {}
        output_params = [param for param in member["params"] if param["is_output"]]
        for index, param in enumerate(output_params):
            if index >= len(output_values):
                break
            serialized[param["name"]] = _serialize_tlb_value(
                output_values[index],
                param["type"],
                depth + 1,
                visited,
            )
        return serialized

    return _serialize_tlb_value(value, member["return_type"], depth + 1, visited)


def _serialize_tlb_value(
    value: Any,
    type_info: Dict[str, Any],
    depth: int,
    visited: set[tuple[str, int]],
) -> Any:
    if value is None or isinstance(value, (bool, float, int, str)):
        return value

    if depth >= MAX_DEPTH:
        return _serialize_value(value, depth)

    type_name = _get_type_name(type_info)
    if type_name and _is_interface_type(type_info):
        visit_key = (type_name, id(value))
        if visit_key in visited:
            return {"interface": type_name, "recursive": True}

        next_visited = set(visited)
        next_visited.add(visit_key)
        return _dump_tlb_interface(value, type_name, depth, next_visited)

    return _serialize_value(value, depth)


def _should_dump_indexed_member(member: Dict[str, Any], dumped: Dict[str, Any]) -> bool:
    if member["name"] in dumped:
        return False
    if member["invoke_kind_name"] != "method":
        return False
    if member["input_param_count"] != 1:
        return False
    if not member["name"].startswith("Get"):
        return False
    return True


def _get_indexed_member_count(
    iface_object: Any,
    members: list[Dict[str, Any]],
    member: Dict[str, Any],
) -> Optional[int]:
    count_member_name = f"{member['name'][3:]}Count"
    count_member = next(
        (
            candidate
            for candidate in members
            if candidate["name"] == count_member_name
            and candidate["invoke_kind_name"] == "property_get"
            and candidate["input_param_count"] == 0
        ),
        None,
    )
    if count_member is None:
        return None

    count = _call_tlb_member(iface_object, count_member)
    if count is None:
        return None

    try:
        return int(count)
    except (TypeError, ValueError):
        return None


def _dump_indexed_member_items(
    iface_object: Any,
    member: Dict[str, Any],
    count: int,
    depth: int,
    visited: set[tuple[str, int]],
) -> Dict[str, Any]:
    items = []
    limit = min(count, MAX_COLLECTION_ITEMS)
    for index in range(limit):
        item = call_method_safe(iface_object, member["name"], index)
        items.append(_serialize_tlb_value(item, member["return_type"], depth + 1, visited))

    return {
        "count": count,
        "items": items,
        "truncated": count > limit,
    }


def _interface_has_geometry_data(interface_name: str) -> bool:
    members = get_interface_members(interface_name)
    if not members:
        return False

    if _interface_is_geometry_like(interface_name):
        return True

    return any(_type_is_geometry(member["return_type"]) for member in members)


def _interface_is_geometry_like(interface_name: str) -> bool:
    if any(token in interface_name for token in GEOMETRY_TYPE_TOKENS):
        return True

    for member in get_interface_members(interface_name):
        if _type_is_geometry(member["return_type"]):
            return True

    return False


def _type_is_geometry(type_info: Dict[str, Any]) -> bool:
    type_name = _get_type_name(type_info)
    if type_name is None:
        return False

    return any(token in type_name for token in GEOMETRY_TYPE_TOKENS)


def _is_interface_type(type_info: Dict[str, Any]) -> bool:
    kind = type_info.get("kind")
    if kind == "pointer":
        target = type_info.get("target")
        if isinstance(target, dict):
            return _is_interface_type(target)
        return False
    return kind in {"interface", "dispatch"}


def _get_type_name(type_info: Dict[str, Any]) -> Optional[str]:
    if "name" in type_info:
        return type_info["name"]

    target = type_info.get("target")
    if isinstance(target, dict):
        return _get_type_name(target)

    return None


def _is_collection_interface(interface_name: str) -> bool:
    members = get_interface_members(interface_name)
    has_count = any(
        member["name"] == "Count" and member["invoke_kind_name"] == "property_get"
        for member in members
    )
    has_get = any(
        member["name"] == "Get" and member["invoke_kind_name"] == "method"
        for member in members
    )
    return has_count and has_get


def _serialize_value(value: Any, depth: int = 0) -> Any:
    if value is None or isinstance(value, (bool, float, int, str)):
        return value

    if hasattr(value, "X") and hasattr(value, "Y") and not hasattr(value, "Z"):
        return {"X": value.X, "Y": value.Y}

    if hasattr(value, "X") and hasattr(value, "Y") and hasattr(value, "Z"):
        return {"X": value.X, "Y": value.Y, "Z": value.Z}

    fields = getattr(value, "_fields_", None)
    if fields:
        result = {}
        for field_name, _ in fields:
            if field_name.startswith("_"):
                continue
            try:
                field_value = getattr(value, field_name)
            except Exception:
                continue
            result[field_name] = _serialize_value(field_value, depth + 1)
        if result:
            return result

    if depth >= MAX_DEPTH:
        return str(value)

    if hasattr(value, "Count") and hasattr(value, "Get"):
        items = []
        count = int(value.Count)
        limit = min(count, MAX_COLLECTION_ITEMS)
        for index in range(limit):
            try:
                items.append(_serialize_value(value.Get(index), depth + 1))
            except (comtypes.COMError, OSError):
                break
        return {
            "count": count,
            "items": items,
            "truncated": count > limit,
        }

    if isinstance(value, (list, tuple)):
        return [_serialize_value(item, depth + 1) for item in value[:MAX_COLLECTION_ITEMS]]

    return str(value)
