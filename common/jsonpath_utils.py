import re
from typing import Any, List


TOKEN_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*|\[\d+\])")


def _tokens(path: str) -> List[str]:
    if not path.startswith("$"):
        raise ValueError(f"json path must start with '$': {path}")
    return TOKEN_PATTERN.findall(path[1:])


def select_json_path(data: Any, path: str) -> Any:
    current = data
    for token in _tokens(path):
        if token.startswith("["):
            index = int(token[1:-1])
            if not isinstance(current, list) or index >= len(current):
                raise KeyError(path)
            current = current[index]
            continue
        if not isinstance(current, dict) or token not in current:
            raise KeyError(path)
        current = current[token]
    return current


def json_path_exists(data: Any, path: str) -> bool:
    try:
        select_json_path(data, path)
        return True
    except (KeyError, IndexError, TypeError, ValueError):
        return False

