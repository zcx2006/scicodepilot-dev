# SciCodePilot Final Status

## Milestones

| Milestone | Status | Summary |
| --- | --- | --- |
| M13 | Done | Benchmark expanded to 6 tasks. |
| M14 | Done | Workspace isolation, hidden evaluator, and score.json. |
| M15 | Done | EnvDoctor for missing_module and missing_file. |
| M16 | Done | Textual reference frontend using BackendController events. |
| M17 | Done | Optional LLM PatchPlanner adapter, default off. |
| M18 | Done | Multi-provider LLM client: mock, deepseek, gemini, openai, disabled. |
| M19 | Done | PatchSafetyReviewer and PatchReviewCreated safety gate. |
| M20 | Done | Showcase and documentation pack. |
| M21 | Done | Benchmark expanded from 6 to 10 tasks. |
| M22 | Done | Ablation experiments and report-ready result tables. |

## Benchmark Tasks

| Task | Category |
| --- | --- |
| `repair_tensor_shape_001` | source-code repair |
| `repair_dtype_mismatch_002` | source-code repair |
| `repair_missing_module_003` | EnvDoctor dependency plan |
| `repair_missing_file_004` | EnvDoctor data/config plan |
| `repair_entrypoint_error_005` | source-code repair |
| `repair_label_shape_006` | source-code repair |
| `repair_device_mismatch_007` | source-code repair |
| `repair_loss_input_008` | source-code repair |
| `repair_collate_fn_009` | source-code repair |
| `repair_config_key_010` | source-code repair |

Source-code repair tasks:

- `repair_tensor_shape_001`
- `repair_dtype_mismatch_002`
- `repair_entrypoint_error_005`
- `repair_label_shape_006`
- `repair_device_mismatch_007`
- `repair_loss_input_008`
- `repair_collate_fn_009`
- `repair_config_key_010`

EnvDoctor tasks:

- `repair_missing_module_003`
- `repair_missing_file_004`

## Expected Results

Current expected test result:

```text
pytest -q: 131 passed
```

The exact test count may grow, but all tests should pass.

Expected suite results:

- diagnosis: `total_tasks=10`, `diagnosis_pass_count=10`
- repair with confirmation: `average_score=1.0`
- repair with confirmation: `patch_review_count=8`
- repair with confirmation: `patch_review_blocked_count=0`
- repair with confirmation: `env_repair_plan_count=2`

## Completed Capabilities

- Stable BackendController public API
- Structured event stream
- Traceback parsing and failure memory
- Rule-based PatchPlanner
- Isolated workspaces
- Hidden evaluator with score.json
- EnvDoctor repair plans
- Textual reference frontend
- Optional LLM PatchPlanner with multi-provider client
- Static PatchSafetyReviewer gate
- M20 showcase and handoff docs
- M22 ablation experiment runner and report table export

## Report Assets

Run:

```bash
python scripts/run_ablation_experiments.py --quick --include-safety
python scripts/export_ablation_tables.py --latest
```

Expected table outputs:

- `outputs/ablations/<timestamp>/ablation_table.md`
- `outputs/ablations/<timestamp>/safety_table.md`
- `report_assets/tables/ablation_table.md`
- `report_assets/tables/safety_table.md`

## Explicitly Not Done

- No OpenHands integration
- No LangGraph agent graph
- No automatic `pip install` or `conda install`
- No automatic missing-file creation
- No LLM default repair path
- No patching of original `benchmark/tasks/*/repo`
