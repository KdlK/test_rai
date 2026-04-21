"""Agent-facing wrappers around Renga application and project lifecycle."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from renga_api.core.app import (
    create_project as core_create_project,
    create_project_style_from_category as core_create_project_style_from_category,
    get_app as core_get_app,
    get_project,
    import_project_category as core_import_project_category,
    open_project as core_open_project,
    quit_app as core_quit_app,
    save_project as core_save_project,
)
from renga_api.core.process import (
    list_renga_processes as core_list_renga_processes,
    stop_all_renga_processes as core_stop_all_renga_processes,
    stop_renga_process as core_stop_renga_process,
)


STDL_CATEGORY_TYPE_IDS = {
    "duct_accessory": "46c07d12-8f76-4537-a473-08d52395baba",
    "duct_fitting": "68eff079-2b52-4e05-a51b-6875d1cdb9fc",
    "electric_distribution_board": "d547f002-4a74-41bf-b1f0-ed8f5846098f",
    "equipment": "4cd3bc4c-14da-43ca-bbc5-d7679566b8dd",
    "lighting_fixture": "c59fd4c5-4050-47a0-b11a-f52c4799470c",
    "mechanical_equipment": "d7e202ce-791c-4123-adbe-5f6357bf85e6",
    "pipe_accessory": "17c36f59-54dc-4440-8b78-034b0adb8716",
    "pipe_fitting": "8b5cf8f2-a391-4701-8cb9-d6a6ba5ee46f",
    "plumbing_fixture": "10bc8911-5931-471a-9c0e-74ad36a7ee8a",
    "wiring_accessory": "2c07d135-8343-418d-a1c2-ea074d98db31",
}

STDL_STYLE_SPECS = {
    "duct_accessory": {
        "collection": "DuctAccessoryStyles",
        "style_type_id": "6c671391-bfea-4e92-9753-8855c05640a0",
    },
    "duct_fitting": {
        "collection": "DuctFittingStyles",
        "style_type_id": "6c6821a0-ebb9-445b-84a2-ed9eb0938e4f",
    },
    "electric_distribution_board": {
        "collection": "ElectricDistributionBoardStyles",
        "style_type_id": "861c0037-7797-43a9-96e7-833a7a2c6ea4",
    },
    "equipment": {
        "collection": "EquipmentStyles",
        "style_type_id": "a369ad70-c1fe-41dd-af3d-bd659ea5b360",
    },
    "lighting_fixture": {
        "collection": "LightingFixtureStyles",
        "style_type_id": "1f85f676-bb99-4a6f-9f72-1789f2f7b362",
    },
    "mechanical_equipment": {
        "collection": "MechanicalEquipmentStyles",
        "style_type_id": "d43c7509-a92c-4e32-bd2d-ba6dd8f5b7a1",
    },
    "pipe_accessory": {
        "collection": "PipeAccessoryStyles",
        "style_type_id": "a31cf7ca-f17b-422a-886a-7a8c362cd49a",
    },
    "pipe_fitting": {
        "collection": "PipeFittingStyles",
        "style_type_id": "b1359bdc-f7ff-43a4-bca0-8d09bc974537",
    },
    "plumbing_fixture": {
        "collection": "PlumbingFixtureStyles",
        "style_type_id": "344299f5-7d7f-43e2-b0a2-1db8e06e8ac8",
    },
    "wiring_accessory": {
        "collection": "WiringAccessoryStyles",
        "style_type_id": "a6e0ba72-acbd-4423-9afc-04d84a09211a",
    },
}


def open_renga(
    mode: Literal["active", "new"] = "active",
    visible: bool = True,
) -> dict[str, Any]:
    """Open Renga or connect to an active instance.

    :param mode: ``active`` to connect to a running instance, ``new`` to start one.
    :param visible: Whether a newly started instance should be visible.
    :returns: Application information for the connected instance.
    """
    if mode == "active":
        processes = core_list_renga_processes()
        if len(processes) > 1:
            process_summary = ", ".join(
                f"pid={item['pid']} title={item['main_window_title']!r}" for item in processes
            )
            raise RuntimeError(
                "Multiple Renga processes are running; active COM connection is ambiguous. "
                f"Close extra instances before calling open_renga(mode='active'): {process_summary}"
            )

    app = core_get_app(mode=mode, visible=visible)
    return {
        "has_project": get_project() is not None,
        "success": True,
        "version": getattr(app, "Version", None),
        "visible": getattr(app, "Visible", None),
    }


def create_model() -> dict[str, Any]:
    """Create a new empty Renga project.

    :returns: Information about the created project.
    """
    project = core_create_project()
    return {
        "project": project,
        "project_path": getattr(project, "Path", None),
        "success": True,
    }


def open_model(path: str) -> dict[str, Any]:
    """Open an existing Renga project from disk.

    :param path: Path to the project file.
    :returns: Information about the opened project.
    """
    project_path = str(Path(path))
    project = core_open_project(project_path)
    return {
        "project": project,
        "project_path": getattr(project, "Path", project_path),
        "success": True,
    }


def save_model(
    path: str,
    overwrite: bool = True,
    project_type: Literal["project", "template"] = "project",
) -> dict[str, Any]:
    """Save the current Renga project to disk.

    :param path: Target path for the saved project.
    :param overwrite: Whether an existing file may be overwritten.
    :param project_type: ``project`` or ``template``.
    :returns: Information about the saved project.
    """
    project_path = str(Path(path))
    project = core_save_project(path=project_path, overwrite=overwrite, project_type=project_type)
    return {
        "project": project,
        "project_path": getattr(project, "Path", project_path),
        "success": True,
    }


def import_stdl_category(path: str, category_type: str) -> dict[str, Any]:
    """Attempt to import a STDL `.rst` category file into the active project.

    Warning: this skill is currently not working end-to-end in the tested Renga
    environment. The underlying COM method ``IProject.ImportCategoryS(...)`` is
    exposed and invoked here, but live checks showed that the call may complete
    without raising while the category still does not appear in the project.
    Treat this wrapper as diagnostic-only until the import path is confirmed.

    :param path: Path to the compiled `.rst` file.
    :param category_type: One of the supported STDL category type names.
    :returns: Diagnostic information about the attempted import call.
    """
    normalized_type = category_type.strip().lower()
    entity_type_id = STDL_CATEGORY_TYPE_IDS.get(normalized_type)
    if entity_type_id is None:
        supported = ", ".join(sorted(STDL_CATEGORY_TYPE_IDS))
        raise ValueError(f"Unsupported category_type={category_type!r}. Supported values: {supported}")

    target_path = str(Path(path))
    entity = core_import_project_category(entity_type_id=entity_type_id, file_path=target_path)
    return {
        "category_type": normalized_type,
        "entity": entity,
        "entity_id": getattr(entity, "Id", None),
        "entity_name": getattr(entity, "Name", None),
        "path": target_path,
        "success": True,
    }


def create_style_from_category(category_type: str, category_id: int) -> dict[str, Any]:
    """Create a category-based MEP style from an existing project category.

    Warning: this skill does not solve STDL import end-to-end by itself. It
    only works after the target category already exists in the current project,
    for example after manual GUI import or when using a built-in category.

    :param category_type: One of the supported STDL category type names.
    :param category_id: Local project identifier of an existing category entity.
    :returns: Information about the created style entity.
    """
    normalized_type = category_type.strip().lower()
    spec = STDL_STYLE_SPECS.get(normalized_type)
    if spec is None:
        supported = ", ".join(sorted(STDL_STYLE_SPECS))
        raise ValueError(f"Unsupported category_type={category_type!r}. Supported values: {supported}")

    entity = core_create_project_style_from_category(
        style_collection_name=spec["collection"],
        style_type_id=spec["style_type_id"],
        category_id=int(category_id),
    )
    return {
        "category_type": normalized_type,
        "category_id": int(category_id),
        "entity": entity,
        "entity_id": getattr(entity, "Id", None),
        "entity_name": getattr(entity, "Name", None),
        "success": True,
    }


def close_renga() -> dict[str, Any]:
    """Close the current Renga application instance.

    :returns: Operation status.
    """
    core_quit_app()
    return {"success": True}


def list_renga_processes() -> dict[str, Any]:
    """List local Renga processes to disambiguate COM instances.

    :returns: Process list with pid, path, and main-window metadata.
    """
    processes = core_list_renga_processes()
    return {
        "count": len(processes),
        "processes": processes,
        "success": True,
    }


def close_renga_process(pid: int, force: bool = True) -> dict[str, Any]:
    """Terminate a specific Renga process by PID.

    :param pid: Target process identifier.
    :param force: Whether the process should be terminated forcefully.
    :returns: Information about the terminated process.
    """
    return core_stop_renga_process(pid=pid, force=force)


def close_all_renga_processes(force: bool = True) -> dict[str, Any]:
    """Terminate all running Renga processes.

    :param force: Whether processes should be terminated forcefully.
    :returns: Summary of terminated process identifiers.
    """
    return core_stop_all_renga_processes(force=force)
