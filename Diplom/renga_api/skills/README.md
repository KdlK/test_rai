# Skills

Agent-facing subpackage built on top of `renga_api.core`.

## Structure

```text
renga_api/
|- core/
`- skills/
   |- __init__.py
   |- catalog.py
   |- catalog_api.py
   |- app.py
   |- model.py
   |- text.py
   |- dump.py
   `- probe.py
```

## Design

- `renga_api.core/*` contains COM-core and low-level helpers.
- `renga_api.skills/*` provides thin wrappers over core functions.
- `renga_api` reexports the main agent-facing API from this subpackage.

## Usage

```python
from renga_api import get_skills_catalog, list_renga_processes, open_renga

processes = list_renga_processes()
open_renga(mode="active")
catalog = get_skills_catalog()
print(processes)
print(catalog)
```
