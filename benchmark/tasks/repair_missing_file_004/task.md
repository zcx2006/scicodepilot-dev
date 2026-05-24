# repair_missing_file_004

This benchmark task contains a minimal training-style script that fails because
a required dataset file is missing.

Public task goals:

- Run the target entry script.
- Inspect the file loading failure.
- Identify the high-level error category.
- Produce a structured failure memory describing the likely cause and next
  repair direction.

Notes:

- This task is diagnosis-only for now.
- Missing data files should not be fabricated by the repair system.
