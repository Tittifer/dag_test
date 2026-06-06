import argparse
import sys
from pathlib import Path

import pytest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run dag-docker-sim-java API tests")
    parser.add_argument("--base-url", default=None, help="API base URL, default comes from conf/config.ini")
    parser.add_argument("--target", default="testcase", help="pytest target path")
    parser.add_argument("--allure", action="store_true", help="write Allure result files to report/temp")
    parser.add_argument("--mark", default=None, help="pytest marker expression, for example 'api and not concurrency'")
    parser.add_argument("--skip-health-check", action="store_true", help="skip service health precheck")
    args, extra = parser.parse_known_args()

    pytest_args = [args.target]
    if args.base_url:
        pytest_args.extend(["--base-url", args.base_url])
    if args.allure:
        Path("report/temp").mkdir(parents=True, exist_ok=True)
        pytest_args.extend(["--alluredir", "report/temp", "--clean-alluredir"])
    if args.mark:
        pytest_args.extend(["-m", args.mark])
    if args.skip_health_check:
        pytest_args.append("--skip-health-check")
    pytest_args.extend(extra)
    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(main())
