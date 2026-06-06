import os

import pytest

from common.paths import REPORT_DIR
from common.yaml_utils import ExtractStore


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=None, help="override API host, for example http://localhost:8080")
    parser.addoption("--keep-extract", action="store_true", default=False, help="keep extract.yaml values between test sessions")


def pytest_configure(config):
    base_url = config.getoption("--base-url")
    if base_url:
        os.environ["DAG_API_HOST"] = base_url
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def clear_extract(request):
    if not request.config.getoption("--keep-extract"):
        ExtractStore().clear()

