# Memory Retrieval Evaluation

These component metrics are for internal controlled benchmark only. They do not claim public benchmark performance, real LLM performance, external baseline comparison, or real-world generalization.

| Query task | Query error type | Query category | Top-1 retrieved memory | Top-1 score | Top-1 error type match | Top-3 contains same error type |
| --- | --- | --- | --- | ---: | --- | --- |
| repair_collate_fn_009 | collate_fn_error | source_code | internal_controlled_repair_collate_fn_009 | 2.7 | yes | yes |
| repair_config_key_010 | config_key_error | source_code | internal_controlled_repair_config_key_010 | 2.7 | yes | yes |
| repair_device_mismatch_007 | device_mismatch | source_code | internal_controlled_repair_device_mismatch_007 | 2.7 | yes | yes |
| repair_dtype_mismatch_002 | dtype_mismatch | source_code | internal_controlled_repair_dtype_mismatch_002 | 2.7 | yes | yes |
| repair_entrypoint_error_005 | entrypoint_error | source_code | internal_controlled_repair_entrypoint_error_005 | 2.7 | yes | yes |
| repair_label_shape_006 | label_shape | source_code | internal_controlled_repair_label_shape_006 | 2.7 | yes | yes |
| repair_loss_input_008 | loss_input_error | source_code | internal_controlled_repair_loss_input_008 | 2.7 | yes | yes |
| repair_missing_file_004 | missing_file | env_data | internal_controlled_repair_missing_file_004 | 2.7 | yes | yes |
| repair_missing_module_003 | missing_module | env_data | internal_controlled_repair_missing_module_003 | 2.7 | yes | yes |
| repair_tensor_shape_001 | tensor_shape | source_code | internal_controlled_repair_tensor_shape_001 | 2.7 | yes | yes |
