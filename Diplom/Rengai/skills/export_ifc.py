"""Навык экспорта проекта в формат IFC."""

from pathlib import Path
import datetime
import os


IFC_EXPORT_PATH = Path(r"C:\MGSU_diplom\IFC")


def export_ifc() -> dict:
    """Экспортирует текущий проект Renga в формат IFC.
    """
    from renga_api.core.app import get_project, get_app

    IFC_EXPORT_PATH.mkdir(parents=True, exist_ok=True)

    # Проверяем подключение
    app = get_app()
    if app is None:
        return {
            "success": False,
            "error": "Renga не запущена. Напиши 'Открыть Renga'.",
        }

    project = get_project()
    if project is None:
        return {
            "success": False,
            "error": "Нет открытого проекта. Открой проект в Renga.",
        }

    try:
        project_path = getattr(project, "Path", None)
        
        if not project_path:
            return {
                "success": False,
                "error": "Проект не сохранён. Сохрани проект (Ctrl+S) и попробуй снова.",
            }

        base_name = Path(project_path).stem
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ifc_filename = f"{base_name}_{timestamp}.ifc"
        ifc_path = IFC_EXPORT_PATH / ifc_filename

        # Экспорт
        result = project.ExportToIfc(str(ifc_path), True)
        
        # Проверяем файл
        if os.path.exists(ifc_path):
            return {
                "success": True,
                "file_path": str(ifc_path),
                "message": f"Экспорт IFC завершён: {ifc_path}",
            }
        else:
            return {
                "success": False,
                "error": "Файл IFC не создан. Попробуй ещё раз.",
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка экспорта: {str(e)}",
        }


if __name__ == "__main__":
    result = export_ifc()
    print(result)