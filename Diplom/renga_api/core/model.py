"""Low-level helpers for Renga model operations."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional

import comtypes

from .app import get_app, get_model, get_project
from .probe import call_method_safe, get_interface

ENTITY_TYPE_IDS = {
    "ILevel": "{C3CE17FF-6F28-411F-B18D-74FE957B2BA8}",
    "IWall": "{4329112A-6B65-48D9-9DA8-ABF1F8F36327}",
}
LEVEL_NAME_PARAMETER_ID = "{1BB1ADDF-A3C0-4356-9525-107EA7DF1513}"


def create_object(args: Any) -> Any:
    """Create a model object inside a project operation."""

    def create(_: Any) -> Any:
        obj = get_model().CreateObject(args)
        if obj is None:
            raise RuntimeError(get_app().LastError or "Failed to create object.")
        return obj

    return run_in_operation(create)


def get_entity_type_id(interface_name: str) -> str:
    """Return the entity type GUID for a known Renga interface name."""
    return ENTITY_TYPE_IDS[interface_name]


def get_model_object_by_id(object_id: int) -> Optional[Any]:
    """Return a model object by id."""
    try:
        return get_model().GetObjects().GetById(object_id)
    except (comtypes.COMError, OSError):
        return None


def list_model_objects() -> list[Any]:
    """Return all objects from the current model."""
    objects = get_model().GetObjects()
    return [objects.GetByIndex(index) for index in range(objects.Count)]


def delete_model_objects_by_id(object_ids: Iterable[int]) -> dict[str, Any]:
    """Delete model objects by local identifiers inside one project operation."""
    ids = [int(object_id) for object_id in object_ids]

    def delete(_: Any) -> dict[str, Any]:
        model = get_model()
        deleted_ids: list[int] = []
        for object_id in ids:
            result = model.DeleteObjectById(object_id)
            if result not in (None, 0):
                raise RuntimeError(f"DeleteObjectById failed for id={object_id} with code {result}")
            deleted_ids.append(object_id)
        return {"deleted_ids": deleted_ids, "deleted_count": len(deleted_ids)}

    return run_in_operation(delete)


def iter_level_objects() -> Iterable[tuple[Any, Any]]:
    """Yield pairs of ``(object, ILevel interface)`` for all levels in the model."""
    for obj in list_model_objects():
        level_iface = get_interface(obj, "ILevel")
        if level_iface is None:
            continue
        yield obj, level_iface


def set_level_name(level: Any, name: str) -> None:
    """Set the level name inside a project operation."""

    def update(_: Any) -> None:
        params = call_method_safe(level, "GetParameters")
        if params is None:
            raise RuntimeError("Level parameter container is unavailable.")

        param = call_method_safe(params, "GetS", LEVEL_NAME_PARAMETER_ID)
        if param is None:
            raise RuntimeError("LevelName parameter is unavailable.")

        result = call_method_safe(param, "SetStringValue", name)
        if result not in (None, 0):
            raise RuntimeError(f"SetStringValue failed with code {result}")

    run_in_operation(update)


def run_in_operation(action: Callable[[Any], Any]) -> Any:
    """Execute an action inside a project operation with rollback on failure."""
    project = get_project()
    if project is None:
        raise RuntimeError("No active Renga project.")

    operation = project.CreateOperation()
    operation.Start()

    try:
        result = action(project)
    except Exception:
        operation.Rollback()
        raise

    operation.Apply()
    return result
