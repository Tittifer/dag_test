from pathlib import Path

import pytest

from base.request_base import RequestBase
from common.yaml_utils import load_case_file


@pytest.mark.business
@pytest.mark.parametrize(
    "base_info,test_case",
    load_case_file(Path(__file__).resolve().parent / "device_register_and_telemetry.yaml"),
    ids=lambda item: item.get("case_name", item.get("api_name", "")),
)
def test_device_register_and_telemetry_flow(base_info, test_case):
    RequestBase().run_case(base_info, test_case)

