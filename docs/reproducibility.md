# Reproducibility Guide

This guide records the commands used to reproduce the current SciCodePilot internal controlled experiments.

## Environment

Project path:

```bash
cd /home/zengl/projects/SciCodePilot
```

Runtime:

- WSL Ubuntu
- Conda environment: `scicodepilot-dev`

Activate the environment before running Python commands:

```bash
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev
```

## Test Suite

Run the full test suite:

```bash
pytest -q
```

## Diagnosis Suite

Run the controlled benchmark in diagnosis mode:

```bash
python scripts/run_experiments.py --mode diagnosis
```

Diagnosis mode validates failure detection, traceback parsing, event emission, and structured `FailureMemory` creation. It does not represent repair performance.

## Repair Without Apply

Run repair planning without modifying the isolated workspace:

```bash
python scripts/run_experiments.py --mode repair
```

This path validates planning, routing, patch proposal, and safety review behavior without applying changes.

## Repair With Confirm Apply

Run repair with explicit apply confirmation:

```bash
python scripts/run_experiments.py --mode repair --confirm-apply
```

This is the main controlled repair path for rule-based repair tasks. It applies approved patches only inside isolated workspaces and must continue to route through `PatchSafetyReviewer`.

## Mock LLM Repair

Run mock LLM repair through the ablation runner:

```bash
python scripts/run_ablation_experiments.py --scenario mock_llm_repair
```

The mock LLM setting verifies that an LLM planner adapter can enter the same safety pipeline. It is not a real LLM evaluation and should not be reported as real LLM model performance.

## Ablation Experiments

Run the current internal controlled ablation suite:

```bash
python scripts/run_ablation_experiments.py --quick --include-safety
```

Current scenarios:

- `diagnosis_only`
- `repair_without_apply`
- `full_rule_based_repair`
- `mock_llm_repair`
- `safety_stress_cases`

These experiments are internal controlled benchmark results. They are not a public benchmark or SOTA comparison.

## Export Ablation Tables

Export report-ready ablation tables from the latest ablation output:

```bash
python scripts/export_ablation_tables.py --latest
```

Expected report asset outputs:

- `report_assets/tables/ablation_table.md`
- `report_assets/tables/safety_table.md`

## Export Repro Manifest

Inspect the latest reproducibility bundle and export a manifest:

```bash
python scripts/export_repro_manifest.py
```

Inspect a specific bundle:

```bash
python scripts/export_repro_manifest.py --bundle-dir artifacts/repro_bundle/20260523_195337
```

Expected manifest outputs:

- `report_assets/tables/repro_bundle_manifest.md`
- `artifacts/repro_bundle/<timestamp>/manifest.md`

The manifest records the bundle path, inspected time, git commit, git status cleanliness, Python version, conda environment files, pip freeze, GPU metadata, Docker metadata, and missing files.

## Scope Statement

The current results come from a 10-task internal controlled benchmark. They show that the current SciCodePilot pipeline solves the designed controlled tasks, but they do not establish public benchmark performance, SOTA repair capability, or external baseline superiority.
