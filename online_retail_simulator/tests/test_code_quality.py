"""Test code quality standards."""

import subprocess
import sys
from pathlib import Path


def test_flake8_compliance():
    """Test that all Python files pass flake8 linting."""
    project_root = Path(__file__).parent.parent.parent
    target_dir = project_root / "online_retail_simulator"

    # Run flake8 on the main package
    result = subprocess.run(
        [sys.executable, "-m", "flake8", str(target_dir)],
        capture_output=True,
        text=True,
        cwd=project_root,
    )

    if result.returncode != 0:
        print(f"flake8 output:\n{result.stdout}")
        print(f"flake8 errors:\n{result.stderr}")

    assert result.returncode == 0, f"flake8 found issues:\n{result.stdout}"
