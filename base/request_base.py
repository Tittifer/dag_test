import json
from copy import deepcopy
from typing import Any, Dict

from common.allure_helper import attach_text, dynamic_title
from common.assertions import Assertions
from common.config import Config
from common.data_loader import deep_merge, read_json_file
from common.http_client import HttpClient
from common.jsonpath_utils import select_json_path
from common.template import replace_template
from common.yaml_utils import ExtractStore


class RequestBase:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.client = HttpClient(self.config)
        self.assertions = Assertions()
        self.extract = ExtractStore()

    def run_case(self, base_info: Dict[str, Any], test_case: Dict[str, Any]) -> Any:
        base_info = replace_template(deepcopy(base_info))
        test_case = replace_template(deepcopy(test_case))

        api_name = base_info.get("api_name", "")
        case_name = test_case.get("case_name", api_name)
        dynamic_title(case_name)

        path = base_info["url"]
        url = path if path.startswith("http") else f"{self.config.api.host}{path}"
        method = base_info.get("method", "GET")
        headers = base_info.get("header") or {}
        cookies = base_info.get("cookies")
        request_payload = self._prepare_request_payload(test_case)

        attach_text("api name", api_name)
        attach_text("case name", case_name)
        attach_text("request url", url)
        attach_text("request method", method)
        attach_text("request headers", headers)
        attach_text("request body", request_payload)

        response = self.client.request(
            name=api_name or case_name,
            method=method,
            url=url,
            headers=headers,
            params=request_payload.get("params"),
            json_body=request_payload.get("json"),
            data=request_payload.get("data"),
            cookies=cookies,
        )
        elapsed_ms = response.elapsed.total_seconds() * 1000
        raw_text = response.text
        try:
            response_body = response.json()
        except ValueError:
            response_body = raw_text

        attach_text("response", response_body)
        self._extract_values(test_case.get("extract"), response_body)
        self.assertions.assert_all(
            expected=test_case.get("validation", []),
            response_body=response_body,
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
            raw_text=raw_text,
        )
        return response_body

    def _prepare_request_payload(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        payload = {key: test_case.get(key) for key in ("params", "json", "data") if key in test_case}
        if "json_file" not in test_case:
            return payload

        json_body = replace_template(read_json_file(test_case["json_file"]))
        json_override = test_case.get("json_override")
        if json_override:
            json_body = deep_merge(json_body, json_override)
        payload["json"] = json_body
        return payload

    def _extract_values(self, extract_rules: Dict[str, str] | None, response_body: Any) -> None:
        if not extract_rules:
            return
        values: Dict[str, Any] = {}
        for key, path in extract_rules.items():
            values[key] = select_json_path(response_body, path)
        self.extract.set_many(values)
        attach_text("extracted values", json.dumps(values, ensure_ascii=False))
