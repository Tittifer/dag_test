import json
import re
from typing import Any, Dict, Iterable, List

from common.db import MysqlClient, RedisClient
from common.jsonpath_utils import json_path_exists, select_json_path
from common.logger import logs


class Assertions:
    def assert_all(
        self,
        expected: Iterable[Dict[str, Any]],
        response_body: Any,
        status_code: int,
        elapsed_ms: float,
        raw_text: str,
    ) -> None:
        for rule in expected or []:
            if len(rule) != 1:
                raise AssertionError(f"invalid assertion rule: {rule}")
            assert_type, value = next(iter(rule.items()))
            handler = getattr(self, f"_assert_{assert_type}", None)
            if handler is None:
                raise AssertionError(f"unsupported assertion type: {assert_type}")
            handler(value, response_body, status_code, elapsed_ms, raw_text)

    def _assert_status_code(self, expected: int, response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        assert status_code == expected, f"expected http status {expected}, got {status_code}"

    def _assert_code(self, expected: int, response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        actual = select_json_path(response_body, "$.code")
        assert actual == expected, f"expected response code {expected}, got {actual}"

    def _assert_message(self, expected: str, response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        actual = select_json_path(response_body, "$.message")
        assert actual == expected, f"expected message {expected!r}, got {actual!r}"

    def _assert_contains(self, expected: str, response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        assert str(expected) in raw_text, f"response does not contain {expected!r}"

    def _assert_jsonpath_eq(self, expected: Dict[str, Any], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_value in expected.items():
            actual = select_json_path(response_body, path)
            assert actual == expected_value, f"{path}: expected {expected_value!r}, got {actual!r}"

    def _assert_jsonpath_in(self, expected: Dict[str, List[Any]], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_values in expected.items():
            actual = select_json_path(response_body, path)
            assert actual in expected_values, f"{path}: expected one of {expected_values!r}, got {actual!r}"

    def _assert_jsonpath_exists(self, expected: List[str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path in expected:
            assert json_path_exists(response_body, path), f"{path} does not exist"

    def _assert_jsonpath_not_empty(self, expected: List[str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path in expected:
            actual = select_json_path(response_body, path)
            assert actual not in (None, "", [], {}), f"{path} is empty"

    def _assert_jsonpath_length(self, expected: Dict[str, int], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_length in expected.items():
            actual = select_json_path(response_body, path)
            actual_length = len(actual)
            assert actual_length == int(expected_length), f"{path}: expected length {expected_length}, got {actual_length}"

    def _assert_jsonpath_min_length(self, expected: Dict[str, int], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, min_length in expected.items():
            actual = select_json_path(response_body, path)
            actual_length = len(actual)
            assert actual_length >= int(min_length), f"{path}: expected length >= {min_length}, got {actual_length}"

    def _assert_jsonpath_max_length(self, expected: Dict[str, int], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, max_length in expected.items():
            actual = select_json_path(response_body, path)
            actual_length = len(actual)
            assert actual_length <= int(max_length), f"{path}: expected length <= {max_length}, got {actual_length}"

    def _assert_jsonpath_greater_than(self, expected: Dict[str, int | float], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_value in expected.items():
            actual = select_json_path(response_body, path)
            assert actual > expected_value, f"{path}: expected > {expected_value}, got {actual}"

    def _assert_jsonpath_greater_or_equal(self, expected: Dict[str, int | float], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_value in expected.items():
            actual = select_json_path(response_body, path)
            assert actual >= expected_value, f"{path}: expected >= {expected_value}, got {actual}"

    def _assert_jsonpath_less_than(self, expected: Dict[str, int | float], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_value in expected.items():
            actual = select_json_path(response_body, path)
            assert actual < expected_value, f"{path}: expected < {expected_value}, got {actual}"

    def _assert_jsonpath_less_or_equal(self, expected: Dict[str, int | float], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_value in expected.items():
            actual = select_json_path(response_body, path)
            assert actual <= expected_value, f"{path}: expected <= {expected_value}, got {actual}"

    def _assert_jsonpath_contains(self, expected: Dict[str, Any], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_value in expected.items():
            actual = select_json_path(response_body, path)
            if isinstance(actual, (dict, list)):
                actual_text = json.dumps(actual, ensure_ascii=False)
                assert str(expected_value) in actual_text, f"{path}: {expected_value!r} not found in JSON node"
            elif isinstance(actual, str):
                assert str(expected_value) in actual, f"{path}: {expected_value!r} not found in {actual!r}"
            else:
                assert actual == expected_value, f"{path}: expected {expected_value!r}, got {actual!r}"

    def _assert_jsonpath_regex(self, expected: Dict[str, str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, pattern in expected.items():
            actual = select_json_path(response_body, path)
            assert re.search(pattern, str(actual)), f"{path}: {actual!r} does not match /{pattern}/"

    def _assert_jsonpath_type(self, expected: Dict[str, str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        for path, expected_type in expected.items():
            actual = select_json_path(response_body, path)
            assert self._matches_type(actual, expected_type), f"{path}: expected type {expected_type}, got {type(actual).__name__}"

    def _assert_response_time_less_than(self, expected_ms: int | float, response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        assert elapsed_ms < float(expected_ms), f"response time {elapsed_ms:.2f}ms >= {expected_ms}ms"

    def _assert_db_exists(self, expected: Dict[str, str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        sql = expected["sql"]
        rows = MysqlClient().query_all(sql)
        logs.info("db assertion sql=%s rows=%s", sql, rows)
        assert rows, f"db assertion has no rows: {sql}"

    def _assert_db_not_exists(self, expected: Dict[str, str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        sql = expected["sql"]
        rows = MysqlClient().query_all(sql)
        assert not rows, f"db assertion unexpectedly returned rows: {sql}"

    def _assert_redis_exists(self, expected: Dict[str, str], response_body: Any, status_code: int, elapsed_ms: float, raw_text: str) -> None:
        key = expected["key"]
        assert RedisClient().exists(key), f"redis key does not exist: {key}"

    @staticmethod
    def _matches_type(actual: Any, expected_type: str) -> bool:
        expected_type = expected_type.lower()
        if expected_type in ("dict", "object"):
            return isinstance(actual, dict)
        if expected_type in ("list", "array"):
            return isinstance(actual, list)
        if expected_type in ("str", "string"):
            return isinstance(actual, str)
        if expected_type in ("int", "integer"):
            return type(actual) is int
        if expected_type in ("float", "double"):
            return type(actual) is float
        if expected_type in ("number", "numeric"):
            return isinstance(actual, (int, float)) and not isinstance(actual, bool)
        if expected_type in ("bool", "boolean"):
            return isinstance(actual, bool)
        if expected_type in ("none", "null"):
            return actual is None
        raise AssertionError(f"unsupported expected type: {expected_type}")
