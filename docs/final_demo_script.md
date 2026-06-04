# Final Demo Script

This script is a terminal plan for the course defense. It uses the internal controlled benchmark and local report assets. It does not require API keys or public benchmark downloads.

## 1. Enter The Project Environment

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev
```

What it demonstrates: the demo runs in the reproducible WSL/conda environment.

What to look for: the shell is inside `/home/zengl/projects/SciCodePilot` and uses `scicodepilot-dev`.

Defense sentence: "All demo commands run in the same local conda environment used for validation."

## 2. Run The Showcase Demo

```bash
python scripts/run_showcase_demo.py
```

What it demonstrates: diagnosis, `FailureMemory`, patch proposal, `PatchReview`, verification, `EnvRepairPlan`, and safety stress summaries.

What to look for: sections named `Source-code repair diagnosis`, `Repair without apply`, `Repair with confirm apply`, `EnvDoctor routing example`, and `Safety stress cases`.

Defense sentence: "This shows the repair pipeline as inspectable events and summaries, not only a final pass/fail score."

## 3. Show Component Metrics

```bash
python scripts/export_component_metrics.py --latest
cat report_assets/tables/component_metrics.md
```

What it demonstrates: report-ready internal controlled benchmark component metrics.

What to look for: `diagnosis pass count | 10/10`, patch counts, env plan counts, and safety stress count.

Defense sentence: "These metrics are internal controlled benchmark metrics and should not be read as public benchmark results."

## 4. Show External Repo Smoke Interface

```bash
python scripts/run_external_repo_smoke.py --help
```

What it demonstrates: there is a local Python repo smoke entry point outside built-in benchmark tasks.

What to look for: `--repo-path`, `--command`, and `--mode {diagnosis,repair-plan}`.

Defense sentence: "The smoke interface copies a local repo into an isolated workspace and does not mutate the original repo."

## 5. Export Failure Memory Records

```bash
python scripts/export_failure_memory_records.py --latest
```

What it demonstrates: internal controlled benchmark cases can be exported into a JSONL memory store.

What to look for: `failure_memory_records_path` and `record_count`.

Defense sentence: "FailureMemory becomes retrievable local memory, stored as JSONL for reproducibility."

## 6. Run Memory Retrieval Demo

```bash
python scripts/run_memory_retrieval_demo.py
```

What it demonstrates: deterministic top-k retrieval and memory-augmented prompt construction.

What to look for: `memory_retrieval_output` and `top_memory`.

Defense sentence: "This is offline token-based retrieval and prompt construction; it does not call a real LLM."

## 7. Run Memory Retrieval Evaluation

```bash
python scripts/evaluate_memory_retrieval.py --latest
```

What it demonstrates: component-level retrieval sanity metrics.

What to look for: `memory_retrieval_eval_output` and `memory_retrieval_eval_table`.

Defense sentence: "The evaluation checks whether internal controlled memory queries recover matching records."

## 8. Run Tests If Time Allows

```bash
pytest -q
```

What it demonstrates: offline deterministic validation across backend, scripts, docs, report assets, and memory retrieval.

What to look for: all tests pass.

Defense sentence: "The test suite validates the controlled benchmark pipeline and report assets without external services."
