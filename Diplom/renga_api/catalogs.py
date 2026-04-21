"""Каталоги констант и справочников для `renga_api`.

Этот модуль предназначен для хранения небольших, стабильных и переиспользуемых
каталогов, которые нужны нескольким agent-facing функциям или могут понадобиться
новым skills в будущем.

Зачем нужен отдельный модуль, а не локальные списки внутри skill-функций:

- catalog не является логикой конкретного skill;
- catalog удобнее проверять и расширять в одном месте;
- agent-facing модули остаются короче и проще;
- легче закрепить единый подход к работе со справочниками проекта.

Какие данные имеет смысл хранить здесь:

- GUID-каталоги quantities, entity types, параметров и подобных стабильных
  констант Renga API;
- небольшие реестры alias-ов и сопоставлений, которые используются больше чем
  в одном сценарии;
- каталоги, которые описывают внешний API и не зависят от состояния текущей
  модели.

Какие данные не стоит хранить здесь:

- runtime-данные конкретного проекта;
- временные результаты диагностики;
- логику вычислений и orchestration;
- значения, которые можно безопасно получить прямым перечислением из живого
  COM-объекта без заранее подготовленного каталога.

Текущее важное ограничение по quantities:

`IQuantityContainer` в рабочем сценарии позволяет проверять наличие quantity по
 GUID и получать её по GUID, но не даёт удобного runtime-перечисления всех
 возможных quantity через интерфейс вида `GetIds()`/`Count`. Поэтому для
 сценариев вроде "покажи доступные метрики" нужен исходный каталог кандидатов,
 по которому можно пройтись и отфильтровать реально поддерживаемые quantities
 через `ContainsS(...)`.
"""

from __future__ import annotations

from typing import Final

# Каталог quantity-кандидатов для `IQuantityContainer`.
#
# Это не список "всех метрик, которые точно есть у любого объекта", а реестр
# известных quantities Renga API, по которым skill может пройтись и проверить
# фактическую поддержку у живого объекта через `ContainsS(...)`.
#
# Структура элемента:
# - `guid`: строковый GUID quantity из документации Renga API;
# - `name`: стабильное англоязычное имя quantity, удобное для вызова skill;
# - `value_kind`: тип значения, который подсказывает, каким методом читать
#   значение из `IQuantity` (`AsArea`, `AsVolume` и т.д.).
#
# Если в проекте появятся другие подобные реестры, их следует добавлять сюда же
# отдельными именованными каталогами, а не разбрасывать по `skills/*`.
QUANTITY_DEFINITIONS: Final[list[dict[str, str]]] = [
    {"guid": "{025f4cef-7b6d-45d9-99e6-2cd851306e03}", "name": "Area", "value_kind": "area"},
    {"guid": "{69b66c34-d411-422d-bd4a-cac3f6846fd8}", "name": "GrossArea", "value_kind": "area"},
    {
        "guid": "{3e5395c2-5f6b-4d58-8349-1419a29a47b9}",
        "name": "GrossCeilingArea",
        "value_kind": "area",
    },
    {
        "guid": "{b38f4236-165a-45ab-8b96-ec0175343404}",
        "name": "GrossCrossSectionArea",
        "value_kind": "area",
    },
    {
        "guid": "{89ab9b57-91b1-4f4a-9a45-9c935882231d}",
        "name": "GrossFloorArea",
        "value_kind": "area",
    },
    {"guid": "{0003e98a-a2f7-4477-89c9-3e9ef6533be3}", "name": "GrossSideArea", "value_kind": "area"},
    {
        "guid": "{269e7b41-3dd9-42d1-b0d0-074e89a3a283}",
        "name": "GrossSideAreaLeft",
        "value_kind": "area",
    },
    {
        "guid": "{9c34e7be-27f7-4950-a51d-dc2d5da8f3e8}",
        "name": "GrossSideAreaRight",
        "value_kind": "area",
    },
    {"guid": "{da41f09a-0e02-40c7-9547-2a0f55b60078}", "name": "GrossVolume", "value_kind": "volume"},
    {"guid": "{4144973d-c4b7-4f11-ab48-8794c9beae43}", "name": "GrossWallArea", "value_kind": "area"},
    {
        "guid": "{a5ca8dfb-13c6-408c-a1c0-61e67026b36b}",
        "name": "InnerSurfaceArea",
        "value_kind": "area",
    },
    {
        "guid": "{7a643dc2-5524-489d-97b3-7011dcbfff48}",
        "name": "InnerSurfaceExternalArea",
        "value_kind": "area",
    },
    {
        "guid": "{1201a2e0-bfb7-4b28-88f6-923571972890}",
        "name": "InnerSurfaceInternalArea",
        "value_kind": "area",
    },
    {"guid": "{0aab4bb0-4645-48d6-9dcb-2aca48577e47}", "name": "NetArea", "value_kind": "area"},
    {"guid": "{e6265c5c-7692-49bd-b7a1-0a5f452feedd}", "name": "NetCeilingArea", "value_kind": "area"},
    {
        "guid": "{5f1efe77-5e2e-450a-a426-efef5b346ecc}",
        "name": "NetCrossSectionArea",
        "value_kind": "area",
    },
    {"guid": "{ea60d526-b527-4896-8e4c-c84a8462b3cc}", "name": "NetFloorArea", "value_kind": "area"},
    {
        "guid": "{65bf3096-b610-4fb0-b603-9e1fd5c21095}",
        "name": "NetFootprintArea",
        "value_kind": "area",
    },
    {"guid": "{6d692b46-fc72-4696-a55e-1d3469aa9d8e}", "name": "NetSideArea", "value_kind": "area"},
    {
        "guid": "{015076c9-4040-45a0-87be-fa4124f6cd4e}",
        "name": "NetSideAreaLeft",
        "value_kind": "area",
    },
    {
        "guid": "{23e7d323-fc29-4b06-8ce7-1bcd2a20f029}",
        "name": "NetSideAreaRight",
        "value_kind": "area",
    },
    {"guid": "{043401f3-0b2f-402a-aca0-826436822405}", "name": "NetVolume", "value_kind": "volume"},
    {"guid": "{c2975e1e-3293-4ad1-8136-316d191b75cc}", "name": "NetWallArea", "value_kind": "area"},
    {"guid": "{fb351198-1a4f-4815-953e-177c17e7641c}", "name": "NominalArea", "value_kind": "area"},
    {
        "guid": "{de1b2227-310d-4652-a793-c799c5be7036}",
        "name": "OuterSurfaceArea",
        "value_kind": "area",
    },
    {
        "guid": "{63afa0b2-3dc4-4500-9ca5-f46fc0ae935a}",
        "name": "TotalSurfaceArea",
        "value_kind": "area",
    },
    {"guid": "{6e63058d-0ab3-4abd-a9ba-574e1746c5ad}", "name": "Volume", "value_kind": "volume"},
]
