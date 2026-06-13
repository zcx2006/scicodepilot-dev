# Contribution Comparison

This table compares system capability dimensions. It does not compare public benchmark scores and does not claim external benchmark superiority.

| Dimension | naive LLM patch script | SciCodePilot |
| --- | --- | --- |
| Structured failure memory | Usually operates directly on raw traceback text. | Converts runtime failures into structured `FailureMemory`. |
| Diagnosis/repair separation | Often combines diagnosis and patch generation in one step. | Supports explicit diagnosis and repair modes. |
| Env/data failure routing | May try to patch code or install packages without clear boundaries. | Routes missing module and missing file cases to `EnvRepairPlan`. |
| Patch safety review | Often applies generated edits without a dedicated static review step. | Reviews proposed patches through `PatchSafetyReviewer`. |
| Isolated workspace | May edit the working tree directly. | Applies approved patches inside isolated workspaces. |
| Event stream | Usually provides limited intermediate observability. | Emits structured events across diagnosis, planning, review, apply, and verification. |
| Reproducibility manifest | Usually not generated as part of the repair flow. | Exports a reproducibility manifest for internal controlled experiments. |
| Public benchmark adapter skeleton | Usually absent or ad hoc. | Provides metadata-only public benchmark pilot placeholders for future evaluation. |

The comparison is limited to architecture and reporting capabilities in this project. It does not state that SciCodePilot has completed public benchmark evaluation.
