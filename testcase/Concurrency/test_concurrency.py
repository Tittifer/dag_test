from pathlib import Path

import pytest

from common.concurrency_runner import ConcurrencyRunner
from common.yaml_utils import read_yaml


@pytest.mark.concurrency
@pytest.mark.parametrize(
    "scenario",
    read_yaml(Path(__file__).resolve().parent / "concurrent_register_telemetry.yaml"),
    ids=lambda item: item.get("case_name", "concurrency"),
)
def test_concurrent_register_and_telemetry(scenario):
    summary = ConcurrencyRunner().run_register_and_telemetry(scenario)
    assert summary["registered_devices"] == scenario["device_count"], summary
    assert summary["error_rate"] <= scenario.get("max_error_rate", 0), summary
    assert summary["p95_ms"] <= scenario.get("max_p95_ms", 5000), summary

