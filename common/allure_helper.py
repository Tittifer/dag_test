import json
from typing import Any


try:
    import allure
except ImportError:  # pragma: no cover
    allure = None


def attach_text(name: str, value: Any) -> None:
    if allure is None:
        return
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, indent=2)
    allure.attach(str(value), name, allure.attachment_type.TEXT)


def dynamic_title(title: str) -> None:
    if allure is None:
        return
    allure.dynamic.title(title)

