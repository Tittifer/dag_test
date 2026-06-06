import os

import pytest
import requests

from common.config import Config
from common.paths import REPORT_DIR
from common.yaml_utils import ExtractStore


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=None, help="override API host, for example http://localhost:8080")
    parser.addoption("--keep-extract", action="store_true", default=False, help="keep extract.yaml values between test sessions")
    parser.addoption("--skip-health-check", action="store_true", default=False, help="skip service health precheck")


def pytest_configure(config):
    base_url = config.getoption("--base-url")
    if base_url:
        os.environ["DAG_API_HOST"] = base_url
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def session_precheck(request):
    if not request.config.getoption("--keep-extract"):
        ExtractStore().clear()
    if not request.config.getoption("--skip-health-check"):
        _check_service_health()


def _check_service_health() -> None:
    config = Config()
    enabled = config.parser.getboolean("health_check", "enabled", fallback=True)
    if not enabled:
        return

    path = config.get("health_check", "path", fallback="/api/health")
    expected_code = config.parser.getint("health_check", "expected_code", fallback=0)
    timeout = config.parser.getfloat("health_check", "timeout", fallback=3.0)
    health_url = f"{config.api.host}{path}"

    try:
        response = requests.get(health_url, timeout=timeout)
    except requests.RequestException as exception:
        pytest.exit(
            f"被测服务不可用：{health_url}\n"
            f"连接异常：{exception}\n"
            "请先启动 dag_docker_sim_java，再重新运行测试。",
            returncode=2,
        )

    if response.status_code != 200:
        pytest.exit(
            f"被测服务健康检查失败：{health_url}\n"
            f"期望 HTTP 200，实际 HTTP {response.status_code}\n"
            f"响应内容：{response.text[:500]}",
            returncode=2,
        )

    try:
        body = response.json()
    except ValueError:
        pytest.exit(
            f"被测服务健康检查失败：{health_url}\n"
            f"响应不是 JSON：{response.text[:500]}",
            returncode=2,
        )

    actual_code = body.get("code")
    if actual_code != expected_code:
        pytest.exit(
            f"被测服务健康检查失败：{health_url}\n"
            f"期望响应 code={expected_code}，实际 code={actual_code}\n"
            f"响应内容：{response.text[:500]}",
            returncode=2,
        )
