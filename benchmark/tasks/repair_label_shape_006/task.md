# repair_label_shape_006

This benchmark task contains a minimal PyTorch classification script that fails
because target labels have a different batch size from the logits.

Public task goals:

- Run the target training-style script.
- Inspect the loss computation failure.
- Identify the high-level error category.
- Produce a structured failure memory and patch plan.

Notes:

- The script runs on CPU and does not require CUDA.
- The repair should align the label batch size with the logits batch size.
