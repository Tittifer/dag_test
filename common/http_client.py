import json
from typing import Any, Dict, Optional

import requests

from common.config import Config
from common.logger import logs


class HttpClient:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.session = requests.Session()

    def request(
        self,
        name: str,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
        data: Any = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        logs.info("request %s %s %s", name, method.upper(), url)
        logs.info("request params=%s json=%s data=%s", params, json_body, data)
        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            cookies=cookies,
            timeout=self.config.api.timeout,
        )
        preview = response.text[:1000]
        try:
            preview = json.dumps(response.json(), ensure_ascii=False)
        except ValueError:
            pass
        logs.info(
            "response %s status=%s elapsed_ms=%.2f body=%s",
            name,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
            preview,
        )
        return response

