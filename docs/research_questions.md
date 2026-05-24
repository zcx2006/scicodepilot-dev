# Research Questions

## Main Question

Can structured failure memory, environment issue routing, and patch safety
review improve the reliability, interpretability, and safety of a scientific
code repair agent?

## Hypotheses

- H1: Structured FailureMemory improves the interpretability of diagnosis and
  repair decisions.
- H2: EnvDoctor prevents `missing_module` and `missing_file` failures from being
  incorrectly treated as source-code patch tasks.
- H3: PatchSafetyReviewer can block dangerous or out-of-bound patches before
  confirmation or application.
- H4: Workspace isolation prevents benchmark contamination and keeps the
  original task repositories reproducible.

## Contributions

1. An event-driven scientific code repair agent backend.
2. Structured failure memory for transparent diagnosis.
3. Routing between source-code repair and environment/data repair plans.
4. A patch safety review gate before confirmation and application.
5. A benchmark suite with workspace isolation and score.json evaluation.
