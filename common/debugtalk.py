import random
import time
import uuid
from typing import Any

from common.yaml_utils import ExtractStore


class DebugTalk:
    def __init__(self):
        self.extract = ExtractStore()

    def get_extract_data(self, key: str, default: str = "") -> Any:
        return self.extract.get(key.strip(), default)

    def timestamp(self) -> int:
        return int(time.time())

    def uuid(self) -> str:
        return uuid.uuid4().hex

    def random_int(self, start: str = "1", end: str = "999999") -> int:
        return random.randint(int(start), int(end))

    def unique_device_name(self, prefix: str = "auto-device") -> str:
        return f"{prefix}-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"

