import subprocess
import sys
from pathlib import Path

import pytest


def test_repair_tensor_shape_task_raises_real_pytorch_shape_error() -> None:
    pytest.importorskip("torch")
    repo_dir = Path("benchmark/tasks/repair_tensor_shape_001/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "mat1 and mat2 shapes cannot be multiplied" in result.stderr
