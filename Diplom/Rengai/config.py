"""Конфигурация для Rengai Chat."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_API_CONFIG: Dict[str, Any] = {
    "base_url": "http://127.0.0.1:11434",
    "api_key": "ollama",
    "model": "llama3.1:8b",
    "max_tokens": 4000,
    "temperature": 0.7,
}

APP_SETTINGS: Dict[str, Any] = {
    "app_name": "Rengai Chat",
    "app_version": "1.0.0",
    "config_dir": Path.home() / ".rengai_chat",
    "history_file": "chat_history.json",
    "max_history_messages": 100,
    "resources_dir": Path(__file__).parent / "resources",
    "skills_dir": Path(__file__).parent / "skills",
}


def read_all_resources() -> str:
    """Читает все ��айлы из папки resources."""
    resources = []
    resources_dir = APP_SETTINGS["resources_dir"]
    
    if not resources_dir.exists():
        return ""
    
    # Text files
    for f in resources_dir.glob("*"):
        if f.suffix.lower() in (".txt", ".md"):
            try:
                content = f.read_text(encoding="utf-8")
                if content:
                    resources.append(f"=== {f.name} ===\n{content}")
            except Exception:
                pass
    
    # PDF files - simple extraction
    for f in resources_dir.glob("*.pdf"):
        try:
            content = extract_from_pdf(f)
            if content:
                resources.append(f"=== {f.name} ===\n{content}")
        except Exception:
            pass
    
    return "\n\n".join(resources)


def extract_from_pdf(pdf_path: Path) -> str:
    """Извлекает текст из PDF."""
    try:
        data = pdf_path.read_bytes()
        chars = []
        for b in data:
            if 32 <= b <= 126 or b in (10, 13, 9):
                chars.append(chr(b))
            else:
                chars.append(' ')
        
        text = ''.join(chars)
        # Clean up spaces
        import re
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text[:3000]
    except Exception:
        return ""


class Config:
    """Конфигурация для Rengai Chat."""

    def __init__(self) -> None:
        self._config_dir = APP_SETTINGS["config_dir"]
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._api_config = DEFAULT_API_CONFIG.copy()
        self._load_api_key()

    def _load_api_key(self) -> None:
        env_key = os.environ.get("OPENAI_API_KEY", "")
        if env_key:
            self._api_config["api_key"] = env_key

    @property
    def api_config(self) -> Dict[str, Any]:
        return self._api_config.copy()

    @property
    def api_key(self) -> str:
        return self._api_config.get("api_key", "")

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._api_config["api_key"] = value
        self._save_api_key()

    def _save_api_key(self) -> None:
        if self._api_config["api_key"]:
            os.environ["OPENAI_API_KEY"] = self._api_config["api_key"]

    @property
    def history_file(self) -> Path:
        return self._config_dir / APP_SETTINGS["history_file"]

    @property
    def resources_dir(self) -> Path:
        return APP_SETTINGS["resources_dir"]

    @property
    def skills_dir(self) -> Path:
        return APP_SETTINGS["skills_dir"]


config = Config()