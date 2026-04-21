"""Executor для выполнения навыков Rengai."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from Rengai.config import config


class SkillsExecutor:
    """Исполнитель навыков для Rengai."""

    def __init__(self) -> None:
        self._skills_cache: Dict[str, Any] = {}
        self._load_skills()

    def _load_skills(self) -> None:
        skills_dir = config.skills_dir
        if not skills_dir.exists():
            return

        for skill_file in skills_dir.glob("*.py"):
            if skill_file.name.startswith("_") or skill_file.name == "__init__.py":
                continue

            skill_name = skill_file.stem
            try:
                relative_path = skill_file.relative_to(Path.cwd())
                module_path = str(relative_path.with_suffix("")).replace("\\", ".")
                spec = importlib.util.find_spec(module_path)
                if spec:
                    self._skills_cache[skill_name] = importlib.import_module(module_path)
            except Exception:
                pass

    def execute(self, action: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет навык по имени.
        :param action: Имя навыка.
        :param args: Аргументы для навыка.
        :returns: Результат выполнения.
        """
        skill_module = self._skills_cache.get(action)
        if skill_module is None:
            return {
                "success": False,
                "error": f"Навык '{action}' не найден",
            }

        try:
            func = getattr(skill_module, action, None)
            if func is None or not callable(func):
                return {
                    "success": False,
                    "error": f"Функция '{action}' не найдена в модуле",
                }

            result = func(**args)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_available_skills(self) -> list[str]:
        """Возвращает список доступных навыков.
        :returns: Список имён навыков.
        """
        return list(self._skills_cache.keys())


skills_executor = SkillsExecutor()