"""Навык открытия Renga."""

from pathlib import Path
from renga_api.skills.app import open_renga as _open_renga


def open_renga(mode: str = "active") -> dict:
    """Открывает Renga или подключается к запущенному экземпляру.
    :param mode: Режим подключения - 'active' для подключения к запущенному,
                'new' для запуска нового экземпляра.
    :returns: Информация о приложении.
    """
    result = _open_renga(mode=mode)
    return result


if __name__ == "__main__":
    result = open_renga()
    print(result)