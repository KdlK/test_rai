# Rengai — ИИ-ассистент для Renga

## Суть проекта

Rengai — это PyQt6-приложение с графическим интерфейсом (GUI), которое предоставляет чат с ИИ-ассистентом для помощи работе в Renga (CAD-программа для BIM-проектирования).

## Структура проекта

```
C:\Diplom\
├── Rengai/              # Приложение чата (PyQt6 GUI)
│   ├── __init__.py     # Инициализация пакета
│   ├── main.py         # Основной код приложения
│   ├── config.py      # Конфигурация
│   ├── context.py     # Управление контекстом
│   ├── llm_client.py  # Клиент для LLM (ollama)
│   ├── skills_executor.py  # Выполнитель навыков
│   ├── resources/     # База знаний (файлы для ответов)
│   └── skills/        # Навыки (skills) для расширения функционала
│
├── renga_api/          # Библиотека для автоматизации Renga через COM
│   ├── __init__.py     # Публичный API
│   ├── core/          # Core-слой (работа с COM)
│   ├── skills/         # Agent-facing функции
│   └── docs/          # Внутренняя документация
│
└── TODO.md            # Журнал задач и изменений
```

## Как запустить

### Вариант 1: Через bat-файл

```powershell
.\Rengai\run.bat
```

### Вариант 2: Через PowerShell

```powershell
cd C:\Diplom
.venv\Scripts\python.exe -m Rengai.main
```

### Вариант 3: Через Start-Process

```powershell
Start-Process ".venv\Scripts\python.exe" -ArgumentList "-m Rengai.main" -WorkingDirectory "C:\Diplom"
```

## Зависимости

- Python 3.10+
- PyQt6 >= 6.0.0
- requests >= 2.28.0
- comtypes >= 1.4.0

## Требования

- Renga Professional (для автоматизации)
- ollama (для локального LLM)