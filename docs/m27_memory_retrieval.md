# M27 FailureMemory Retrieval

M27 upgrades `FailureMemory` from a one-run structured record into a lightweight retrievable memory mechanism. The goal is to preserve successful internal controlled repair cases as local JSONL records, retrieve similar cases deterministically, and use the retrieved examples to build a memory-augmented structured `PatchPlan` prompt.

This pack remains offline and deterministic. It does not make real LLM calls, require an API key, install packages, download public benchmarks, or change the default benchmark path.

## What M27 Adds

- `FailureMemoryRecord`: a JSON-serializable dataclass for historical failure and repair metadata.
- `FailureMemoryStore`: a JSONL-backed memory store with save, load, append, list, and top-k retrieval.
- Embedding-free retrieval using lowercase token overlap plus deterministic bonuses for matching `error_type`, `exception_type`, and path-like terms.
- `export_failure_memory_records.py`: exports conservative records from internal controlled task metadata and available ablation summaries.
- `memory_prompt_builder.py`: builds a deterministic memory-augmented prompt for a future structured `PatchPlan` planner.
- `run_memory_retrieval_demo.py`: runs an offline retrieval demo and writes summary and prompt artifacts.

## JSONL Memory Records

Memory records are written to:

```text
artifacts/failure_memory/memory_records.jsonl
```

Each row is one `FailureMemoryRecord` with fields such as `record_id`, `task_id`, `error_type`, `failure_category`, `command`, `exception_type`, `error_message`, `traceback_summary`, `root_cause_hypothesis`, `repair_action`, `patch_plan_summary`, `verification_success`, `score`, `created_from`, and `metadata`.

The exporter is conservative. If detailed patch or failure data are not present in the ablation summary, missing fields remain `None` or are recorded in `metadata`. The exported records are scoped to the internal controlled benchmark.

## Retrieval

Retrieval is deterministic and embedding-free:

1. Tokenize query and record text into lowercase alphanumeric/path-like tokens.
2. Compute token overlap.
3. Add a bonus for exact `error_type` match.
4. Add a bonus for exact `exception_type` match.
5. Add a smaller bonus for matching path-like tokens.
6. Sort by descending score, then by `record_id` ascending for stable tie-breaking.

An empty store is valid and returns no retrieved records. Malformed JSONL raises a clear `ValueError` with the line number.

## Memory-augmented Prompt Construction

`build_memory_augmented_patch_prompt()` accepts a current `FailureMemoryRecord` and retrieved examples. It returns deterministic plain text that instructs a future planner to output only structured `PatchPlan` JSON.

The prompt includes explicit safety constraints:

- no shell execution
- no dependency installation
- no fake data creation
- no absolute paths
- no path traversal
- no benchmark/test/output modification
- patch must still pass `PatchSafetyReviewer`

The prompt includes compact summaries of retrieved records only. It does not include huge file contents, secrets, or environment variables.

## Demo

Run:

```bash
python scripts/export_failure_memory_records.py --latest
python scripts/run_memory_retrieval_demo.py
```

The demo writes:

```text
outputs/memory_retrieval/<timestamp>/summary.md
outputs/memory_retrieval/<timestamp>/summary.json
outputs/memory_retrieval/<timestamp>/prompt.md
```

## Safety And Reproducibility

M27 does not apply patches. It only exports memory records, retrieves similar records, and constructs a prompt for future planning. Any future patch still needs the existing safety pipeline and `PatchSafetyReviewer`.

The memory store is local JSONL, so it is easy to inspect, archive, and reproduce. Retrieval uses deterministic string matching, so repeated runs over the same records and query should produce the same ordering.

## Limitations

- Retrieval is embedding-free and simple.
- There is no real LLM evaluation yet.
- Memory-augmented planning is not the default benchmark path.
- The records are derived from the internal controlled benchmark, not from public benchmark evaluation.
- M27 does not claim public benchmark results, external baseline comparison, or real-world generalization.
