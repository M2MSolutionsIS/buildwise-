"""
Run pytest and save results to docs/test_results.txt.
Usage: python scripts/run_tests.py
"""

import subprocess
import sys
import os
from datetime import datetime

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "test_results.txt")


def main():
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

    print("Running pytest...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )

    output = f"BuildWise Test Results — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    output += "=" * 60 + "\n\n"
    output += result.stdout
    if result.stderr:
        output += "\n\nSTDERR:\n" + result.stderr

    output += f"\n\nExit code: {result.returncode}\n"

    with open(RESULTS_PATH, "w") as f:
        f.write(output)

    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    print(f"\nResults saved to: {RESULTS_PATH}")
    print(f"Exit code: {result.returncode}")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
