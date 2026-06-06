from pathlib import Path

import pytest

from base.request_base import RequestBase
from common.yaml_utils import load_case_file


CASE_FILES = [
    "health.yaml",
    "topology.yaml",
    "fusions.yaml",
    "cloud_ledger.yaml",
    "fusion_ledger.yaml",
    "devices.yaml",
    "register_device.yaml",
    "submit_telemetry_negative.yaml",
]


def _load_cases():
    current_dir = Path(__file__).resolve().parent
    cases = []
    for file_name in CASE_FILES:
        cases.extend(load_case_file(current_dir / file_name))
    return cases


@pytest.mark.api
@pytest.mark.parametrize("base_info,test_case", _load_cases(), ids=lambda item: item.get("case_name", item.get("api_name", "")))
def test_single_interface(base_info, test_case):
    RequestBase().run_case(base_info, test_case)

