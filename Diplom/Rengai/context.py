"""Управление контекстом чата."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from Rengai.config import config


class ContextManager:
    """Менеджер контекста чата."""

    def __init__(self) -> None:
        self._messages: List[Dict[str, str]] = []
        self._last_command: Optional[Dict[str, Any]] = None
        self._load_history()

    def _load_history(self) -> None:
        if config.history_file.exists():
            try:
                with open(config.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._messages = data.get("messages", [])
            except Exception:
                self._messages = []

    def _save_history(self) -> None:
        from Rengai.config import APP_SETTINGS
        try:
            data = {"messages": self._messages[-100:]}
            with open(config.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        if include_system:
            return self._messages
        return [m for m in self._messages if m.get("role") != "system"]

    def add_message(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self._save_history()

    def clear_history(self) -> None:
        self._messages = []
        self._save_history()

    def set_last_command(self, command: Dict[str, Any]) -> None:
        self._last_command = command

    def get_last_command(self) -> Optional[Dict[str, Any]]:
        return self._last_command


context_manager = ContextManager()