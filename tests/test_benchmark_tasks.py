import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.task_loader import load_benchmark_task


def test_load_all_ten_tasks() -> None:
    task_ids = [
        "repair_tensor_shape_001",
        "repair_dtype_mismatch_002",
        "repair_missing_module_003",
        "repair_missing_file_004",
        "repair_entrypoint_error_005",
        "repair_label_shape_006",
        "repair_device_mismatch_007",
        "repair_loss_input_008",
        "repair_collate_fn_009",
        "repair_config_key_010",
    ]

    tasks = [
        load_benchmark_task(Path("benchmark/tasks") / task_id)
        for task_id in task_ids
    ]

    assert [task.task_id for task in tasks] == task_ids


def test_missing_module_task_fails_with_module_not_found() -> None:
    repo_dir = Path("benchmark/tasks/repair_missing_module_003/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr


def test_dtype_mismatch_task_fails_with_dtype_error() -> None:
    pytest.importorskip("torch")
    repo_dir = Path("benchmark/tasks/repair_dtype_mismatch_002/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert any(
        pattern in result.stderr
        for pattern in [
            "same dtype",
            "expected scalar type",
            "Found dtype",
        ]
    )


def test_missing_file_task_fails_with_file_not_found() -> None:
    repo_dir = Path("benchmark/tasks/repair_missing_file_004/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr


def test_entrypoint_error_task_fails_with_name_error() -> None:
    repo_dir = Path("benchmark/tasks/repair_entrypoint_error_005/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "NameError" in result.stderr
    assert "mainn" in result.stderr


def test_label_shape_task_fails_with_label_batch_error() -> None:
    pytest.importorskip("torch")
    repo_dir = Path("benchmark/tasks/repair_label_shape_006/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Expected input batch_size" in result.stderr


def test_device_mismatch_task_fails_with_device_error() -> None:
    repo_dir = Path("benchmark/tasks/repair_device_mismatch_007/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Expected all tensors to be on the same device" in result.stderr


def test_loss_input_task_fails_with_loss_input_error() -> None:
    repo_dir = Path("benchmark/tasks/repair_loss_input_008/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "loss_input_error" in result.stderr


def test_collate_fn_task_fails_with_collate_error() -> None:
    repo_dir = Path("benchmark/tasks/repair_collate_fn_009/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "collate_fn_error" in result.stderr


def test_config_key_task_fails_with_config_key_error() -> None:
    repo_dir = Path("benchmark/tasks/repair_config_key_010/repo")

    result = subprocess.run(
        [sys.executable, "train.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "config_key_error" in result.stderr
