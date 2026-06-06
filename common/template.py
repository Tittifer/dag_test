import json
import re
from typing import Any

from common.debugtalk import DebugTalk


FUNC_PATTERN = re.compile(r"\$\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)\((?P<args>[^}]*)\)\}")


def _call_func(match: re.Match[str]) -> str:
    func_name = match.group("name")
    raw_args = match.group("args").strip()
    args = [] if raw_args == "" else [item.strip() for item in raw_args.split(",")]
    func = getattr(DebugTalk(), func_name)
    value = func(*args)
    return "" if value is None else str(value)


def replace_template(data: Any) -> Any:
    if data is None:
        return None
    if isinstance(data, str):
        return FUNC_PATTERN.sub(_call_func, data)
    raw = json.dumps(data, ensure_ascii=False)
    replaced = FUNC_PATTERN.sub(_call_func, raw)
    return json.loads(replaced)

