# Memory Retrieval Evaluation Summary

- Memory path: `/home/zengl/projects/SciCodePilot/artifacts/failure_memory/memory_records.jsonl`
- Record count: 10
- Top-k: 3
- Claim scope: internal controlled benchmark only; component-level retrieval sanity evaluation; not public benchmark; not real LLM evaluation; not external baseline comparison

## Metrics

| Metric | Value |
| --- | --- |
| total_queries | 10 |
| top1_self_match_count | 10 |
| top3_self_match_count | 10 |
| top1_error_type_match_count | 10 |
| top3_error_type_match_count | 10 |
| top1_failure_category_match_count | 10 |
| top3_failure_category_match_count | 10 |
| source_repair_query_count | 8 |
| env_or_data_query_count | 2 |
| average_top1_score | 2.7 |
| average_top3_score | 1.418509 |
| empty_result_count | 0 |

## Compact Results

| Query record | Query error type | Top-1 memory | Top-1 score |
| --- | --- | --- | ---: |
| internal_controlled_repair_collate_fn_009 | collate_fn_error | internal_controlled_repair_collate_fn_009 | 2.7 |
| internal_controlled_repair_config_key_010 | config_key_error | internal_controlled_repair_config_key_010 | 2.7 |
| internal_controlled_repair_device_mismatch_007 | device_mismatch | internal_controlled_repair_device_mismatch_007 | 2.7 |
| internal_controlled_repair_dtype_mismatch_002 | dtype_mismatch | internal_controlled_repair_dtype_mismatch_002 | 2.7 |
| internal_controlled_repair_entrypoint_error_005 | entrypoint_error | internal_controlled_repair_entrypoint_error_005 | 2.7 |
| internal_controlled_repair_label_shape_006 | label_shape | internal_controlled_repair_label_shape_006 | 2.7 |
| internal_controlled_repair_loss_input_008 | loss_input_error | internal_controlled_repair_loss_input_008 | 2.7 |
| internal_controlled_repair_missing_file_004 | missing_file | internal_controlled_repair_missing_file_004 | 2.7 |
| internal_controlled_repair_missing_module_003 | missing_module | internal_controlled_repair_missing_module_003 | 2.7 |
| internal_controlled_repair_tensor_shape_001 | tensor_shape | internal_controlled_repair_tensor_shape_001 | 2.7 |

## Claim Boundary

- not public benchmark
- not real LLM evaluation
- not external baseline comparison
- not a generalization claim
