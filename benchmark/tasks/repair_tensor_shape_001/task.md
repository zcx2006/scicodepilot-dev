# repair_tensor_shape_001

This benchmark task contains a minimal PyTorch training-style script that fails
because a classifier head expects 128 input features while the upstream tensor
contains only 64 features.

Public task goals:

- Run the target training entry script.
- Inspect the runtime failure.
- Identify the high-level error category.
- Produce a structured failure memory describing the likely cause and next
  repair direction.

Notes:

- In M6 this task remains diagnosis-only.
- No code patch is expected yet.
- The expected diagnosis is stored separately for evaluation.
- The script runs on CPU and does not require CUDA.
