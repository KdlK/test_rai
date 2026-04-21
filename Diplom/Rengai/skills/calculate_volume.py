"""Навык вычисления объёма элементов."""

from renga_api.skills.model import get_object_ids_by_category, get_model_object_by_id
from renga_api.core.app import get_project, get_app
from renga_api.core.probe import call_method_safe, get_property_safe
import comtypes.gen.Renga as Renga


CATEGORY_VOLUME_METRIC = {
    "walls": "Volume",
    "floors": "Volume",
    "columns": "Volume",
}

WALL_HEIGHT_PARAM = "{0C6C933C-E47C-40D2-BA84-B8AE5CCEC6F1}"
WALL_THICKNESS_PARAM = "{25548335-7030-43B1-B602-9898F3ADC3B0}"


def detect_category_from_text(text: str) -> str | None:
    """Определяет категорию элементов по тексту пользователя."""
    text_lower = text.lower().strip()

    walls_keywords = ["стен", "стены", "wall", "walls"]
    floors_keywords = ["плит", "плиты", "перекрыт", "пол", "floor", "floors"]
    columns_keywords = ["колонн", "колонны", "колонна", "column", "columns"]

    for kw in walls_keywords:
        if kw in text_lower:
            return "walls"
    for kw in floors_keywords:
        if kw in text_lower:
            return "floors"
    for kw in columns_keywords:
        if kw in text_lower:
            return "columns"

    return None


def calculate_volume(category: str) -> dict:
    """Вычисляет суммарный объём элементов указанной категории.
    :param category: Категория элементов - 'walls', 'floors', 'columns'.
    :returns: Словарь с суммарным объёмом.
    """
    try:
        project = get_project()
    except Exception:
        project = None

    if project is None:
        return {
            "category": category,
            "element_count": 0,
            "total_volume": 0.0,
            "elements": [],
            "success": False,
            "error": "Не могу найти открытый проект. Откройте проект в Renga.",
        }

    normalized = category.strip().lower()

    category_map = {
        "walls": "IWallParams",
        "wall": "IWallParams",
        "стены": "IWallParams",
        "стена": "IWallParams",
        "floors": "IFloor",
        "floor": "IFloor",
        "перекрытия": "IFloor",
        "перекрытие": "IFloor",
        "columns": "IColumn",
        "column": "IColumn",
        "колонны": "IColumn",
        "колонна": "IColumn",
    }

    interface_name = category_map.get(normalized)
    if interface_name is None:
        supported = ", ".join(sorted(category_map.keys()))
        return {
            "category": category,
            "element_count": 0,
            "total_volume": 0.0,
            "elements": [],
            "success": False,
            "error": f"Неизвестная категория: {category}. Поддерживаются: {supported}",
        }

    result = get_object_ids_by_category(interface_name)
    object_ids = result.get("object_ids", [])

    if not object_ids:
        return {
            "category": normalized,
            "element_count": 0,
            "total_volume": 0.0,
            "elements": [],
            "success": True,
            "message": "Элементы не найдены.",
        }

    total_volume = 0.0
    element_details = []
    errors = []

    if normalized in ["walls", "стены", "перекрытия"]:
        for obj_id in object_ids:
            try:
                volume = _calculate_wall_volume(obj_id)
                if volume > 0:
                    total_volume += volume
                    element_details.append({"id": obj_id, "volume": volume})
            except Exception as e:
                errors.append(f"Ошибка элемента {obj_id}: {e}")

    elif normalized in ["columns", "колонны"]:
        for obj_id in object_ids:
            try:
                volume = _calculate_column_volume(obj_id)
                if volume > 0:
                    total_volume += volume
                    element_details.append({"id": obj_id, "volume": volume})
                else:
                    element_details.append({"id": obj_id, "volume": "N/A"})
            except Exception as e:
                errors.append(f"Ошибка колонны {obj_id}: {e}")

    else:
        for obj_id in object_ids:
            try:
                volume = _calculate_generic_volume(obj_id)
                if volume > 0:
                    total_volume += volume
                    element_details.append({"id": obj_id, "volume": volume})
            except Exception as e:
                errors.append(f"Ошибка элемента {obj_id}: {e}")

    return {
        "category": normalized,
        "element_count": len(element_details),
        "total_volume": total_volume,
        "elements": element_details,
        "success": True,
        "message": f"Найдено {len(element_details)} элементов. Общий объём: {total_volume:.3f} м³",
    }


def _calculate_wall_volume(obj_id: int) -> float:
    """Вычисляет объём стены."""
    from renga_api.skills.model import get_model_object_by_id
    from renga_api.core.probe import get_property_safe
    
    obj = get_model_object_by_id(obj_id)
    if not obj:
        return 0.0
    
    # Get parameters - height and thickness
    height = 0.0
    thickness = 0.0
    
    params = call_method_safe(obj, "GetParameters")
    if params:
        height_param = call_method_safe(params, "GetS", WALL_HEIGHT_PARAM)
        if height_param:
            try:
                height = height_param.GetDoubleValue() / 1000.0  # mm to meters
            except:
                pass
        
        thickness_param = call_method_safe(params, "GetS", WALL_THICKNESS_PARAM)
        if thickness_param:
            try:
                thickness = thickness_param.GetDoubleValue() / 1000.0  # mm to meters
            except:
                pass
    
    # Get length from bounding box
    bbox = get_property_safe(obj, "BoundingBox")
    if bbox:
        try:
            length = bbox.Size.X / 1000.0  # meters
            height = height if height > 0 else bbox.Size.Z / 1000.0  # Use Z if height not found
            volume = length * thickness * height
            return volume
        except:
            pass
    
    # Fallback: calculate from footprint area
    try:
        footprint = get_property_safe(obj, "FootprintArea")
        if footprint:
            area = footprint.Value if hasattr(footprint, 'Value') else footprint
            volume = (area / 1e6) * height if height > 0 else 0
            return volume
    except:
        pass
    
    # If we have height and thickness but no length, estimate as minimum
    if height > 0 and thickness > 0:
        return height * thickness * 1.0  # Assume 1m length as minimum
    
    return 0.0


def _calculate_column_volume(obj_id: int) -> float:
    """Вычисляет объём колонны."""
    from renga_api.skills.model import get_model_object_by_id
    from renga_api.core.probe import call_method_safe, get_property_safe

    obj = get_model_object_by_id(obj_id)
    if not obj:
        return 0.0

    # Try to get quantity (if calculated)
    try:
        quantities = call_method_safe(obj, "GetQuantities")
        if quantities:
            guid = "6e63058d-0ab3-4abd-a9ba-574e1746c5ad"  # Volume
            if quantities.ContainsS(guid):
                q = quantities.GetS(guid)
                if q and q.HasValue:
                    return float(q.AsVolume(Renga.VolumeUnit_Meters3))
    except:
        pass

    # Otherwise estimate from bounding box
    bbox = get_property_safe(obj, "BoundingBox")
    if bbox:
        try:
            dx = bbox.Size.X / 1000.0
            dy = bbox.Size.Y / 1000.0
            dz = bbox.Size.Z / 1000.0
            return dx * dy * dz
        except:
            pass

    return 0.0


def _calculate_generic_volume(obj_id: int) -> float:
    """Вычисляет объём любого элемента."""
    from renga_api.skills.model import get_model_object_by_id
    from renga_api.core.probe import call_method_safe, get_property_safe

    obj = get_model_object_by_id(obj_id)
    if not obj:
        return 0.0

    # Try quantity first
    try:
        quantities = call_method_safe(obj, "GetQuantities")
        if quantities:
            guid = "6e63058d-0ab3-4abd-a9ba-574e1746c5ad"
            if quantities.ContainsS(guid):
                q = quantities.GetS(guid)
                if q and q.HasValue:
                    return float(q.AsVolume(Renga.VolumeUnit_Meters3))
    except:
        pass

    # Use bounding box
    bbox = get_property_safe(obj, "BoundingBox")
    if bbox:
        try:
            dx = bbox.Size.X / 1000.0
            dy = bbox.Size.Y / 1000.0
            dz = bbox.Size.Z / 1000.0
            return dx * dy * dz
        except:
            pass

    return 0.0


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: calculate_volume.py <category>")
        print("Categories: walls, floors, columns")
        sys.exit(1)

    category = sys.argv[1]
    result = calculate_volume(category)
    print(result)