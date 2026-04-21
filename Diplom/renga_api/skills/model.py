"""Agent-facing wrappers around model operations."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from renga_api.catalogs import QUANTITY_DEFINITIONS
from renga_api.core.app import get_app, get_model
from renga_api.core.model import (
    create_object,
    delete_model_objects_by_id,
    get_entity_type_id,
    get_model_object_by_id,
    iter_level_objects,
    list_model_objects,
    run_in_operation,
    set_level_name,
)
from renga_api.core.probe import call_method_safe, get_interface, get_property_safe, has_interface

WALL_HEIGHT_PARAMETER_ID = "{0C6C933C-E47C-40D2-BA84-B8AE5CCEC6F1}"
WALL_THICKNESS_PARAMETER_ID = "{25548335-7030-43B1-B602-9898F3ADC3B0}"
CATEGORY_INTERFACE_ALIASES = {
    "level": "ILevel",
    "level_object": "ILevelObject",
    "wall": "IWallParams",
}


def create_level(elevation: float = 0.0, name: Optional[str] = None) -> Dict[str, Any]:
    """Create a level in the active Renga project.

    :param elevation: Level elevation in model units.
    :param name: Optional level name.
    :returns: Creation result with identifiers and actual elevation.
    """
    from comtypes.gen import Renga

    model = get_model()
    args = model.CreateNewEntityArgs()
    args.TypeIdS = get_entity_type_id("ILevel")

    placement = Renga.Placement3D()
    placement.Origin = Renga.Point3D(0.0, 0.0, float(elevation))
    placement.xAxis = Renga.Vector3D(1.0, 0.0, 0.0)
    placement.zAxis = Renga.Vector3D(0.0, 0.0, 1.0)
    args.Placement3D = placement

    level = create_object(args)
    level_iface = get_interface(level, "ILevel")

    if name:
        set_level_name(level, name)
        level_iface = get_interface(level, "ILevel")

    actual_elevation = get_property_safe(level_iface, "Elevation")
    if actual_elevation is not None and abs(float(actual_elevation) - float(elevation)) > 0.001:
        raise RuntimeError(
            f"Level created at elevation {actual_elevation}, requested {float(elevation)}. "
            "Current COM creation path does not apply non-zero level elevation."
        )

    return {
        "elevation": actual_elevation,
        "level_id": level.Id,
        "name": get_property_safe(level_iface, "LevelName"),
        "success": True,
    }


def create_wall(
    level_id: int,
    start_x: float = 0.0,
    start_y: float = 0.0,
    end_x: float = 5000.0,
    end_y: float = 0.0,
    thickness: float = 200.0,
    height: float = 3000.0,
) -> Dict[str, Any]:
    """Create a wall between two points on the given level.

    :param level_id: Host level identifier.
    :param start_x: Start point X in model units.
    :param start_y: Start point Y in model units.
    :param end_x: End point X in model units.
    :param end_y: End point Y in model units.
    :param thickness: Wall thickness in model units.
    :param height: Wall height in model units.
    :returns: Creation result with wall id and applied parameters.
    """
    from comtypes.gen import Renga

    def create(_: Any) -> Any:
        model = get_model()
        args = model.CreateNewEntityArgs()
        args.TypeIdS = get_entity_type_id("IWall")
        args.HostObjectId = int(level_id)
        wall = model.CreateObject(args)
        if wall is None:
            raise RuntimeError("CreateObject returned no wall object.")

        baseline_object = get_interface(wall, "IBaseline2DObject")
        if baseline_object is None:
            raise RuntimeError("Wall does not expose IBaseline2DObject.")

        line = get_app().Math.CreateLineSegment2D(
            Renga.Point2D(float(start_x), float(start_y)),
            Renga.Point2D(float(end_x), float(end_y)),
        )
        baseline_result = call_method_safe(baseline_object, "SetBaseline", line)
        if baseline_result not in (None, 0):
            raise RuntimeError(f"SetBaseline failed with code {baseline_result}")

        _set_parameter_double(wall, WALL_HEIGHT_PARAMETER_ID, height)
        _set_parameter_double(wall, WALL_THICKNESS_PARAMETER_ID, thickness)
        return wall

    wall = run_in_operation(create)
    wall_params = get_interface(wall, "IWallParams")

    return {
        "end": {"X": float(end_x), "Y": float(end_y)},
        "height": get_property_safe(wall_params, "Height"),
        "level_id": int(level_id),
        "start": {"X": float(start_x), "Y": float(start_y)},
        "success": True,
        "thickness": get_property_safe(wall_params, "Thickness"),
        "wall_id": wall.Id,
    }


def find_base_level() -> Optional[int]:
    """Find the first level at elevation 0.

    :returns: Level id or ``None`` when the base level is absent.
    """
    for level in get_levels():
        elevation = level["elevation"]
        if elevation is not None and abs(float(elevation)) < 0.001:
            return level["id"]
    return None


def get_all_objects() -> List[Any]:
    """Return all model objects from the active project.

    :returns: List of COM objects from the current model.
    """
    return list_model_objects()


def get_levels() -> List[Dict[str, Any]]:
    """Return all levels from the active project.

    :returns: List of level descriptors.
    """
    levels = []
    for obj, level_iface in iter_level_objects():
        levels.append(
            {
                "elevation": get_property_safe(level_iface, "Elevation"),
                "id": obj.Id,
                "name": get_property_safe(level_iface, "LevelName"),
                "unique_id": get_property_safe(obj, "UniqueIdS"),
            }
        )
    return levels


def get_object_by_id(object_id: int) -> Optional[Any]:
    """Return a model object by its identifier.

    :param object_id: Model object id.
    :returns: COM object or ``None`` when nothing is found.
    """
    return get_model_object_by_id(object_id)


def get_object_ids_by_category(category: str) -> Dict[str, Any]:
    """Return object ids for the requested category.

    :param category: Category alias such as ``wall`` or ``level``, or a raw interface name.
    :returns: Matching object ids and the resolved interface name.
    """
    resolved_category = _resolve_category_interface_name(category)
    object_ids: list[int] = []

    for obj in list_model_objects():
        if has_interface(obj, resolved_category):
            object_ids.append(int(obj.Id))

    return {
        "category": category,
        "interface_name": resolved_category,
        "object_ids": object_ids,
        "count": len(object_ids),
        "success": True,
    }


def delete_objects_by_id(object_ids: List[int]) -> Dict[str, Any]:
    """Delete model objects by their local identifiers.

    :param object_ids: List of local model object ids to delete.
    :returns: Summary of deleted object ids.
    """
    result = delete_model_objects_by_id(object_ids)
    return {
        "deleted_count": result["deleted_count"],
        "deleted_ids": result["deleted_ids"],
        "success": True,
    }


def list_available_object_metrics(
    category: Optional[str] = None,
    object_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Вернуть список доступных quantity-метрик для объектов.

    Эта функция использует каталог `renga_api.catalogs.QUANTITY_DEFINITIONS`
    как источник известных quantity-кандидатов, а затем проверяет их
    фактическую доступность у живых объектов через `IQuantityContainer`.

    :param category: Имя категории объектов, например ``wall``.
    :param object_ids: Явный список локальных id объектов.
    :returns: Список доступных метрик и статистику их доступности.
    """
    target_object_ids = _resolve_target_object_ids(category=category, object_ids=object_ids)
    metrics_by_name: dict[str, Dict[str, Any]] = {}

    for object_id in target_object_ids:
        quantity_container = _get_object_quantity_container(object_id)
        if quantity_container is None:
            continue

        for definition in QUANTITY_DEFINITIONS:
            quantity = _get_supported_quantity(quantity_container, definition["guid"])
            if quantity is None:
                continue

            entry = metrics_by_name.setdefault(
                definition["name"],
                {
                    "guid": definition["guid"],
                    "has_value_count": 0,
                    "name": definition["name"],
                    "supported_count": 0,
                    "text": getattr(quantity, "Text", None),
                    "type": getattr(quantity, "Type", None),
                    "unit": _get_metric_unit(definition["value_kind"]),
                    "value_kind": definition["value_kind"],
                },
            )
            entry["supported_count"] += 1
            if bool(getattr(quantity, "HasValue", False)):
                entry["has_value_count"] += 1

    metrics = sorted(metrics_by_name.values(), key=lambda item: item["name"])
    return {
        "category": category,
        "metrics": metrics,
        "metric_count": len(metrics),
        "object_count": len(target_object_ids),
        "object_ids": target_object_ids,
        "success": True,
    }


def get_object_metric_value(
    metric_name: str,
    category: Optional[str] = None,
    object_ids: Optional[List[int]] = None,
    aggregation: Literal["sum", "list"] = "sum",
) -> Dict[str, Any]:
    """Вернуть значение quantity-метрики по имени.

    Эта функция использует каталог `renga_api.catalogs.QUANTITY_DEFINITIONS`
    как реестр известных quantity GUID и имён, после чего выбирает нужную
    метрику и читает её значение через `IQuantityContainer` у живых объектов.

    :param metric_name: Имя метрики, например ``NetVolume`` или локализованный ``Text``.
    :param category: Имя категории объектов, например ``wall``.
    :param object_ids: Явный список локальных id объектов.
    :param aggregation: ``sum`` для суммы по объектам или ``list`` для значений по каждому объекту.
    :returns: Значение метрики и диагностическую информацию по объектам.
    """
    target_object_ids = _resolve_target_object_ids(category=category, object_ids=object_ids)
    definition = _resolve_quantity_definition(metric_name=metric_name, object_ids=target_object_ids)

    values: list[Dict[str, Any]] = []
    missing_object_ids: list[int] = []
    total_value = 0.0

    for object_id in target_object_ids:
        quantity_container = _get_object_quantity_container(object_id)
        if quantity_container is None:
            missing_object_ids.append(object_id)
            continue

        quantity = _get_supported_quantity(quantity_container, definition["guid"])
        if quantity is None or not bool(getattr(quantity, "HasValue", False)):
            missing_object_ids.append(object_id)
            continue

        value = _read_quantity_value(quantity, definition["value_kind"])
        values.append({"object_id": object_id, "value": value})
        total_value += float(value)

    result: Dict[str, Any] = {
        "aggregation": aggregation,
        "category": category,
        "metric": {
            "guid": definition["guid"],
            "name": definition["name"],
            "unit": _get_metric_unit(definition["value_kind"]),
            "value_kind": definition["value_kind"],
        },
        "missing_count": len(missing_object_ids),
        "missing_object_ids": missing_object_ids,
        "object_count": len(target_object_ids),
        "object_ids": target_object_ids,
        "success": True,
        "value_count": len(values),
    }

    if aggregation == "sum":
        result["value"] = total_value
    else:
        result["values"] = values

    return result


def _set_parameter_double(obj: Any, parameter_id: str, value: float) -> None:
    params = call_method_safe(obj, "GetParameters")
    if params is None:
        raise RuntimeError("Object parameter container is unavailable.")

    param = call_method_safe(params, "GetS", parameter_id)
    if param is None:
        raise RuntimeError(f"Parameter {parameter_id} is unavailable.")

    result = call_method_safe(param, "SetDoubleValue", float(value))
    if result not in (None, 0):
        raise RuntimeError(f"SetDoubleValue failed for parameter {parameter_id} with code {result}")


def _resolve_category_interface_name(category: str) -> str:
    normalized = category.strip()
    if not normalized:
        raise ValueError("Category must be a non-empty string.")

    alias = CATEGORY_INTERFACE_ALIASES.get(normalized.lower())
    if alias is not None:
        return alias
    return normalized


def _resolve_target_object_ids(
    category: Optional[str],
    object_ids: Optional[List[int]],
) -> List[int]:
    if object_ids:
        return [int(object_id) for object_id in object_ids]

    if category:
        result = get_object_ids_by_category(category)
        return [int(object_id) for object_id in result["object_ids"]]

    raise ValueError("Either category or object_ids must be provided.")


def _get_object_quantity_container(object_id: int) -> Any:
    obj = get_object_by_id(int(object_id))
    if obj is None:
        return None
    return call_method_safe(obj, "GetQuantities")


def _get_supported_quantity(quantity_container: Any, quantity_guid: str) -> Any:
    if quantity_container is None:
        return None

    if not bool(call_method_safe(quantity_container, "ContainsS", quantity_guid)):
        return None

    return call_method_safe(quantity_container, "GetS", quantity_guid)


def _resolve_quantity_definition(metric_name: str, object_ids: List[int]) -> Dict[str, str]:
    normalized_metric_name = metric_name.strip().casefold()
    if not normalized_metric_name:
        raise ValueError("metric_name must be a non-empty string.")

    for definition in QUANTITY_DEFINITIONS:
        if normalized_metric_name in {
            definition["name"].casefold(),
            definition["guid"].casefold(),
        }:
            return definition

    matched_definition: Optional[Dict[str, str]] = None
    for object_id in object_ids:
        quantity_container = _get_object_quantity_container(object_id)
        if quantity_container is None:
            continue

        for definition in QUANTITY_DEFINITIONS:
            quantity = _get_supported_quantity(quantity_container, definition["guid"])
            if quantity is None:
                continue

            quantity_text = getattr(quantity, "Text", None)
            if isinstance(quantity_text, str) and quantity_text.strip().casefold() == normalized_metric_name:
                if matched_definition is None:
                    matched_definition = definition
                    continue
                if matched_definition["guid"] != definition["guid"]:
                    raise ValueError(
                        f"Metric name {metric_name!r} is ambiguous for available quantities."
                    )

    if matched_definition is not None:
        return matched_definition

    supported_names = ", ".join(definition["name"] for definition in QUANTITY_DEFINITIONS)
    raise ValueError(
        f"Unsupported metric_name={metric_name!r}. Supported quantity names: {supported_names}"
    )


def _read_quantity_value(quantity: Any, value_kind: str) -> float:
    from comtypes.gen import Renga

    if value_kind == "area":
        return float(quantity.AsArea(Renga.AreaUnit_Meters2))
    if value_kind == "volume":
        return float(quantity.AsVolume(Renga.VolumeUnit_Meters3))
    raise ValueError(f"Unsupported value_kind={value_kind!r}")


def _get_metric_unit(value_kind: str) -> str:
    if value_kind == "area":
        return "m2"
    if value_kind == "volume":
        return "m3"
    return "unknown"
