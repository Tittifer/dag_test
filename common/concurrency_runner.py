from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from statistics import mean
from time import perf_counter
from typing import Any, Dict, List

from common.config import Config
from common.http_client import HttpClient


@dataclass
class OperationResult:
    success: bool
    elapsed_ms: float
    body: Any
    error: str = ""


class ConcurrencyRunner:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.client = HttpClient(self.config)

    def run_register_and_telemetry(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        terminal_id = scenario.get("terminal_id", "fusion1")
        device_count = int(scenario.get("device_count", 10))
        concurrency = int(scenario.get("concurrency", 5))
        telemetry_per_device = int(scenario.get("telemetry_per_device", 1))

        register_results = self._run_many(
            [lambda index=index: self._register(terminal_id, index) for index in range(device_count)],
            concurrency,
        )
        device_ids = [
            item.body["data"]["device_id"]
            for item in register_results
            if item.success and isinstance(item.body, dict)
        ]
        telemetry_tasks = []
        for device_id in device_ids:
            for sequence in range(telemetry_per_device):
                telemetry_tasks.append(lambda device_id=device_id, sequence=sequence: self._telemetry(terminal_id, device_id, sequence))
        telemetry_results = self._run_many(telemetry_tasks, concurrency)
        all_results = register_results + telemetry_results
        success_count = sum(1 for item in all_results if item.success)
        total_count = len(all_results)
        latencies = [item.elapsed_ms for item in all_results]
        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95) - 1 if sorted_latencies else 0
        return {
            "total": total_count,
            "success": success_count,
            "failed": total_count - success_count,
            "error_rate": 0 if total_count == 0 else (total_count - success_count) / total_count,
            "avg_ms": mean(latencies) if latencies else 0,
            "p95_ms": sorted_latencies[max(p95_index, 0)] if sorted_latencies else 0,
            "max_ms": max(latencies) if latencies else 0,
            "registered_devices": len(device_ids),
        }

    def _run_many(self, tasks: List[Any], concurrency: int) -> List[OperationResult]:
        results: List[OperationResult] = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(task) for task in tasks]
            for future in as_completed(futures):
                results.append(future.result())
        return results

    def _register(self, terminal_id: str, index: int) -> OperationResult:
        body = {
            "deviceName": f"concurrent-device-{index}",
            "useBootstrapIdentity": False,
            "autoConfirm": True,
        }
        return self._post(f"/api/fusions/{terminal_id}/devices/register", body)

    def _telemetry(self, terminal_id: str, device_id: str, sequence: int) -> OperationResult:
        body = {
            "dataPayload": {
                "sequence": sequence,
                "device_name": device_id,
                "captured_at": perf_counter(),
                "metrics": {
                    "voltage_v": 228.4,
                    "current_a": 16.2,
                    "temperature_c": 33.8,
                    "active_power_kw": 3.701,
                },
            }
        }
        return self._post(f"/api/fusions/{terminal_id}/devices/{device_id}/telemetry", body)

    def _post(self, path: str, body: Dict[str, Any]) -> OperationResult:
        started = perf_counter()
        try:
            response = self.client.request(
                name=path,
                method="POST",
                url=f"{self.config.api.host}{path}",
                headers={"Content-Type": "application/json"},
                json_body=body,
            )
            elapsed_ms = (perf_counter() - started) * 1000
            payload = response.json()
            return OperationResult(
                success=response.status_code == 200 and payload.get("code") == 0,
                elapsed_ms=elapsed_ms,
                body=payload,
            )
        except Exception as exception:
            return OperationResult(False, (perf_counter() - started) * 1000, None, str(exception))

