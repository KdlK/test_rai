"""Connection helpers for the running Renga COM application."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

import comtypes.client

PROG_ID = "Renga.Application.1"

_app: Optional[Any] = None


def get_app(*, mode: Literal["active", "new"] = "active", visible: bool = True, force_new: bool = False) -> Any:
    """Return a cached COM application object."""
    global _app

    if _app is not None and not force_new:
        return _app

    if mode == "active":
        try:
            _app = comtypes.client.GetActiveObject(PROG_ID)
        except Exception:
            if force_new:
                _app = None
            else:
                raise
    else:
        _app = comtypes.client.CreateObject(PROG_ID)
        _app.Visible = visible

    return _app


def create_project() -> Any:
    """Create a new empty project in the current application instance."""
    app = get_app(mode="new")
    result = app.CreateProject()
    if result != 0:
        raise RuntimeError(f"CreateProject failed with code {result}")
    return app.Project


def open_project(path: str | Path) -> Any:
    """Open a project file and return the loaded project."""
    app = get_app(mode="new")
    project_path = str(Path(path))
    result = app.OpenProject(project_path)
    if result != 0:
        raise RuntimeError(f"OpenProject failed with code {result} for {project_path}")
    return app.Project


def save_project(
    path: str | Path,
    *,
    overwrite: bool = True,
    project_type: Literal["project", "template"] = "project",
) -> Any:
    """Save the current project to disk and return the saved project."""
    project = get_project()
    if project is None:
        raise RuntimeError("No active Renga project.")

    target_path = str(Path(path))
    project_type_id = 0 if project_type == "project" else 1
    result = project.SaveAs(target_path, project_type_id, bool(overwrite))
    if result != 0:
        raise RuntimeError(f"SaveAs failed with code {result} for {target_path}")
    return project


def import_project_category(entity_type_id: str, file_path: str | Path) -> Any:
    """Import a STDL category into the current project and return the created entity."""
    project = get_project()
    if project is None:
        raise RuntimeError("No active Renga project.")

    target_path = str(Path(file_path))
    return project.ImportCategoryS(str(entity_type_id), target_path)


def create_project_style_from_category(
    *,
    style_collection_name: str,
    style_type_id: str,
    category_id: int,
) -> Any:
    """Create a new category-based project style inside an operation."""
    project = get_project()
    if project is None:
        raise RuntimeError("No active Renga project.")

    collection = getattr(project, style_collection_name)
    operation = project.StartOperation()
    try:
        args = collection.CreateNewEntityArgs()
        args.CategoryId = int(category_id)
        args.TypeIdS = str(style_type_id)
        entity = collection.Create(args)
        if entity is None:
            raise RuntimeError(get_app().LastError or "Failed to create category-based style.")
        operation.Apply()
        return entity
    except Exception:
        operation.Rollback()
        raise


def get_project() -> Any:
    """Return the current project or ``None`` if nothing is open."""
    return get_app().Project


def get_model() -> Any:
    """Return the current project model."""
    project = get_project()
    if project is None:
        raise RuntimeError("No active Renga project.")
    return project.Model


def get_selection() -> Any:
    """Return the current selection object."""
    return get_app().Selection


def quit_app() -> None:
    """Close the cached application instance."""
    global _app
    if _app is not None:
        _app.Quit()
        _app = None


def reset_connection() -> None:
    """Drop the cached application instance."""
    global _app
    _app = None
