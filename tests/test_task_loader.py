import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scicodepilot.eval.task_loader import load_benchmark_task


def test_load_repair_tensor_shape_task() -> None:
    task_dir = Path("benchmark/tasks/repair_tensor_shape_001")

    task = load_benchmark_task(task_dir)

    assert task.task_id == "repair_tensor_shape_001"
    assert task.entry_command == "python train.py"
    assert task.repo_dir.endswith("repair_tensor_shape_001/repo")
    assert task.expected_diagnosis_path.endswith("expected_diagnosis.json")
    assert "torch" in task.requires
