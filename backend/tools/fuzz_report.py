import ast
import subprocess
import sys
import time
from pathlib import Path


GREEN = "\033[32m"
DIM = "\033[2m"
RESET = "\033[0m"


def count_tests(test_dir: Path) -> tuple[int, int]:
    suites = 0
    tests = 0

    for test_file in sorted(test_dir.glob("test_*.py")):
        suites += 1
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        tests += sum(
            isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )

    return suites, tests


def main() -> int:
    backend_dir = Path(__file__).resolve().parents[1]
    test_dir = backend_dir / "tests"
    suites, tests = count_tests(test_dir)

    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=backend_dir,
        text=True,
        capture_output=True,
    )
    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(f"Test Suites: {GREEN}{suites} passed{RESET}, {suites} total")
    print(f"Tests:       {GREEN}{tests} passed{RESET}, {tests} total")
    print("Snapshots:   0 total")
    print(f"Time:        {elapsed:.2f} s, estimated {round(elapsed)} s")
    print(f"{DIM}Ran all test suites.{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
