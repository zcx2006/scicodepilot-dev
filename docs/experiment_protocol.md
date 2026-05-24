# Experiment Protocol

## Benchmark Tasks

| Task | Error Type | Category |
| --- | --- | --- |
| `repair_tensor_shape_001` | `tensor_shape` | source-code repair |
| `repair_dtype_mismatch_002` | `dtype_mismatch` | source-code repair |
| `repair_missing_module_003` | `missing_module` | env/data diagnosis |
| `repair_missing_file_004` | `missing_file` | env/data diagnosis |
| `repair_entrypoint_error_005` | `entrypoint_error` | source-code repair |
| `repair_label_shape_006` | `label_shape` | source-code repair |
| `repair_device_mismatch_007` | `device_mismatch` | source-code repair |
| `repair_loss_input_008` | `loss_input_error` | source-code repair |
| `repair_collate_fn_009` | `collate_fn_error` | source-code repair |
| `repair_config_key_010` | `config_key_error` | source-code repair |

Eight source-code repair tasks are expected to produce PatchPlan,
PatchReviewCreated, PatchApplied after confirmation, and score.json. Two
env/data diagnosis tasks are expected to produce EnvRepairPlanCreated rather
than source patches.

## Metrics

- `diagnosis_success_count`
- `diagnosis_pass_count`
- `patch_plan_count`
- `patch_review_count`
- `patch_review_blocked_count`
- `patch_applied_count`
- `verification_success_count`
- `env_repair_plan_count`
- `scored_task_count`
- `average_score`

## Experimental Settings

1. Rule-based planner baseline in diagnosis mode.
2. Rule-based planner repair without apply, using `confirm_apply=False`.
3. Rule-based planner repair with confirm apply, using `confirm_apply=True`.
4. Mock LLM planner repair with `SCICODEPILOT_LLM_PROVIDER=mock`.
5. Safety reviewer cases from `tests/test_patch_safety_reviewer.py`.

## Ablation Commands

```bash
python scripts/run_ablation_experiments.py --quick --include-safety
python scripts/export_ablation_tables.py --latest
```

The export command writes report-ready tables to:

- `outputs/ablations/<timestamp>/ablation_table.md`
- `outputs/ablations/<timestamp>/safety_table.md`
- `report_assets/tables/ablation_table.md`
- `report_assets/tables/safety_table.md`

## Hidden Evaluator Limitation

The current hidden evaluator is intentionally minimal. It mainly checks the
benchmark entry command behavior and writes score.json. It should not be
overstated as a comprehensive hidden test suite.

## Contamination Check

After experiments, confirm original benchmark bugs remain in
`benchmark/tasks/*/repo`:

```bash
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py
```
