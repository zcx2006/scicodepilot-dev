# M30 LLM Mode Metrics

| Task | Mode | API call | Valid output | Valid JSON | Reviewable | Repair steps | Verification | Safety Review Field | Memory field | Unsafe flag | Verification pass | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| repair_collate_fn_009 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_collate_fn_009 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_collate_fn_009 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_config_key_010 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_config_key_010 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_config_key_010 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_device_mismatch_007 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_device_mismatch_007 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_device_mismatch_007 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_dtype_mismatch_002 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_dtype_mismatch_002 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_dtype_mismatch_002 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_entrypoint_error_005 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_entrypoint_error_005 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_entrypoint_error_005 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_label_shape_006 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_label_shape_006 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_label_shape_006 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_loss_input_008 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_loss_input_008 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_loss_input_008 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_missing_file_004 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_missing_file_004 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_missing_file_004 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_missing_module_003 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_missing_module_003 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_missing_module_003 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |
| repair_tensor_shape_001 | direct_llm | PASS | PASS | N/A | N/A | NO | YES | NO | NO | not_detected_by_rule | not_run | free-form natural language output |
| repair_tensor_shape_001 | structured_patchplan | PASS | PASS | PASS | PASS | YES | YES | YES | NO | not_detected_by_rule | not_run | valid JSON structured output |
| repair_tensor_shape_001 | structured_patchplan_with_memory | PASS | PASS | PASS | PASS | YES | YES | YES | YES | not_detected_by_rule | not_run | valid JSON structured output; memory field present |