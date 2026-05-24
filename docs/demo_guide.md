# SciCodePilot Demo Guide

## Enter The Project

```bash
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
```

All commands should run inside WSL Ubuntu and the `scicodepilot-dev` conda env.

## Run Tests

```bash
pytest -q
```

## Run Benchmark Suites

Diagnosis suite:

```bash
python scripts/run_benchmark_suite.py --mode diagnosis
```

Repair suite without applying patches:

```bash
python scripts/run_benchmark_suite.py --mode repair
```

Repair suite with confirmation:

```bash
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

Mock LLM repair suite:

```bash
SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

## Run M20 Showcase

Quick showcase:

```bash
python scripts/run_showcase.py
```

Smoke test:

```bash
python scripts/run_showcase.py --smoke-test
```

Full showcase:

```bash
python scripts/run_showcase.py --full
```

Showcase with mock LLM planner:

```bash
python scripts/run_showcase.py --use-mock-llm
```

## Run Textual Frontend

Smoke test:

```bash
python scripts/run_textual_app.py --smoke-test
```

Interactive app:

```bash
python scripts/run_textual_app.py
```

## Check Original Benchmark Integrity

```bash
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py
```

Expected lines include:

- `classifier_expected_dim = 128`
- `dtype=torch.float64`
- `mainn()`
- `batch_size + 1`

## Recommended Classroom Flow

1. Run `python scripts/run_showcase.py`.
2. Show `PatchReviewCreated` between `PatchProposed` and approval/apply.
3. Show `EnvRepairPlanCreated` for `repair_missing_module_003`.
4. Run `python scripts/run_benchmark_suite.py --mode repair --confirm-apply`.
5. Show original benchmark integrity checks.

## Recording Suggestion

Record the M20 showcase first, then briefly open the Textual reference frontend,
then show `docs/architecture.md` to explain the system boundaries.
