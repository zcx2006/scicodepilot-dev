# Memory Retrieval Examples

These examples describe the intended behavior of the deterministic, embedding-free memory retrieval layer. They are for internal controlled benchmark analysis only and do not claim public benchmark improvement or real LLM performance.

| Query failure | Top retrieved memory | Why it matched | Intended planner benefit |
| ------------- | -------------------- | -------------- | ------------------------ |
| `tensor_shape` matrix multiplication mismatch | `internal_controlled_repair_tensor_shape_001` | Exact `error_type` match plus shared tensor and shape terms. | Remind a future planner to align downstream layer dimensions with upstream feature dimensions. |
| `missing_module` import failure | `internal_controlled_repair_missing_module_003` | Exact `error_type` and dependency-related terms. | Route to `EnvRepairPlan` instead of unsafe installation or source-code patching. |
| `missing_file` data/config path failure | `internal_controlled_repair_missing_file_004` | Exact `error_type` and file/path terms. | Route to data/config availability guidance without creating fake data. |
| `config_key_error` missing config key | `internal_controlled_repair_config_key_010` | Exact `error_type` and shared config-key terms. | Suggest inspecting key names before proposing a small source-code patch. |

All retrieved examples remain advisory. Any generated patch must still pass `PatchSafetyReviewer`.
