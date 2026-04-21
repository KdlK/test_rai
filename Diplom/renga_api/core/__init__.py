"""Minimal public API for the Renga core package."""

from .app import (
    create_project,
    create_project_style_from_category,
    get_app,
    get_model,
    get_project,
    get_selection,
    import_project_category,
    open_project,
    quit_app,
    reset_connection,
    save_project,
)
from .dump import dump_object, dump_selected_object
from .model import (
    create_object,
    delete_model_objects_by_id,
    get_entity_type_id,
    get_model_object_by_id,
    list_model_objects,
    run_in_operation,
)
from .process import list_renga_processes, stop_all_renga_processes, stop_renga_process
from .probe import (
    call_method_safe,
    get_interface,
    get_property_safe,
    has_interface,
    probe_interfaces,
)
from .typelib import get_interface_registry, get_typelib
from .utils import dump_to_file, guid_to_str, save_json

__version__ = "0.1.0"

__all__ = [
    "call_method_safe",
    "create_object",
    "create_project",
    "create_project_style_from_category",
    "delete_model_objects_by_id",
    "dump_object",
    "dump_selected_object",
    "dump_to_file",
    "get_app",
    "get_entity_type_id",
    "get_interface",
    "get_interface_registry",
    "get_model",
    "get_model_object_by_id",
    "get_project",
    "get_property_safe",
    "get_selection",
    "get_typelib",
    "import_project_category",
    "guid_to_str",
    "has_interface",
    "list_model_objects",
    "list_renga_processes",
    "open_project",
    "probe_interfaces",
    "quit_app",
    "reset_connection",
    "run_in_operation",
    "save_json",
    "save_project",
    "stop_all_renga_processes",
    "stop_renga_process",
]
