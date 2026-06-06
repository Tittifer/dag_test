from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from common.paths import EXTRACT_FILE


def read_yaml(path: str | Path) -> Any:
    yaml_path = Path(path)
    with yaml_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data if data is not None else {}


def write_yaml(path: str | Path, data: Any) -> None:
    yaml_path = Path(path)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with yaml_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


def load_case_file(path: str | Path) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    raw_cases = read_yaml(path)
    result: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for block in raw_cases:
        base_info = block.get("baseInfo", {})
        for test_case in block.get("testCase", []):
            result.append((base_info, test_case))
    return result


class ExtractStore:
    def __init__(self, path: str | Path = EXTRACT_FILE):
        self.path = Path(path)

    def clear(self) -> None:
        write_yaml(self.path, {})

    def all(self) -> Dict[str, Any]:
        data = read_yaml(self.path) if self.path.exists() else {}
        return data if isinstance(data, dict) else {}

    def get(self, key: str, default: Any = "") -> Any:
        return self.all().get(key, default)

    def set_many(self, values: Dict[str, Any]) -> None:
        current = self.all()
        current.update(values)
        write_yaml(self.path, current)

