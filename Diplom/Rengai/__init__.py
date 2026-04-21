"""Rengai - Чат с ИИ-ассистентом для Renga."""

import sys
from pathlib import Path

_parent = Path(__file__).parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

__version__ = "1.0.0"