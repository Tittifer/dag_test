import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from common.paths import ROOT_DIR


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT_DIR / candidate


def read_json_file(path: str | Path) -> Any:
    json_path = resolve_project_path(path)
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def deep_merge(base: Any, override: Any) -> Any:
    if not isinstance(base, dict) or not isinstance(override, dict):
        return deepcopy(override)

    merged: Dict[str, Any] = deepcopy(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged

