# repair_dtype_mismatch_002

This benchmark task contains a minimal PyTorch script that fails because a
matrix multiplication receives tensors with incompatible dtypes.

Public task goals:

- Run the target training-style entry script.
- Inspect the runtime failure.
- Identify the high-level error category.
- Produce a structured failure memory describing the likely cause and next
  repair direction.

Notes:

- This task is diagnosis-first and can be repaired by aligning tensor dtypes.
- The script runs on CPU and does not require CUDA.
