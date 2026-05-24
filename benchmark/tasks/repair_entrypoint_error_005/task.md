# repair_entrypoint_error_005

This benchmark task contains a minimal Python script where the entrypoint call
is misspelled.

Public task goals:

- Run the target entry script.
- Inspect the NameError failure.
- Identify the high-level error category.
- Produce a structured failure memory and patch plan for the typo.

Notes:

- The script defines `main()` but incorrectly calls `mainn()`.
- The repair plan should correct the entrypoint call.
