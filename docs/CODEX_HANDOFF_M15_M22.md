# SciCodePilot M15-M22 Codex 代码仓库级交接文档

本文档用于给下一位 Codex/GPT 继续维护 SciCodePilot。它不是聊天摘要，而是代码仓库级技术交接文档，重点记录 M15-M22 的实际工程语义、稳定接口、验证命令、当前限制和后续工作边界。

> 本轮生成文档时，尝试通过 WSL 执行仓库读取命令但收到 `Wsl/Service/E_ACCESSDENIED`。因此本文档以用户提供的当前项目状态、本对话历史和既有里程碑约束为准；下一位 Codex 接手后应先按第 13 节运行验证命令复核。

## 1. 项目基本信息

- 项目名：SciCodePilot
- 项目路径：`/home/zengl/projects/SciCodePilot`
- 运行环境：WSL Ubuntu
- Conda 环境：`scicodepilot-dev`
- 标准进入命令：

```bash
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
```

所有项目命令必须在 WSL Ubuntu 中运行，不要在 Windows PowerShell 中运行。涉及 Python / pip 时，优先使用当前 conda 环境中的 `python` / `pip`。

## 2. 当前项目一句话定位

SciCodePilot 当前定位为：

> A structured failure-memory agent for reliable scientific code repair and reproducibility.

中文：

> 面向可靠科研代码修复与复现的结构化失败记忆 Agent 系统。

它不是普通聊天机器人，也不是简单 API wrapper，而是一个 event-driven scientific code diagnosis/repair benchmark system：从 benchmark 任务出发，在隔离 workspace 中执行命令、解析失败、生成结构化 FailureMemory、给出安全审查后的修复计划，并通过事件流和实验汇总产物支持前端、评测和报告。

## 3. 当前核心 Pipeline

```text
benchmark task
  -> workspace copy
  -> run command
  -> parse stderr/stdout
  -> FailureMemory
  -> EnvDoctor or PatchPlanner
  -> PatchSafetyReviewer
  -> confirmation
  -> workspace apply
  -> verification
  -> hidden evaluator
  -> score.json
  -> event stream / experiment summary
```

关键约束：

- source-code bug 走 `PatchPlanner`，生成 `PatchPlan` 和 unified diff。
- `missing_module` / `missing_file` 走 `EnvDoctor`，生成 `EnvRepairPlanCreated`，不生成源码 patch。
- 所有 `PatchPlan` 都必须经过 `PatchSafetyReviewer`。
- `repair` 的 apply 只允许发生在 `outputs/workspaces/<run_id>/<task_id>/repo`。
- `benchmark/tasks/*/repo` 必须始终保持原始 bug 状态。

## 4. Public API Contract

前端和外部调用方应只依赖以下稳定入口：

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
```

`BackendController` 当前 public API 必须保持不变：

```python
list_tasks() -> list[TaskInfo]
get_task(task_id: str) -> BenchmarkTask
run_task(task_id: str, mode: str, confirm_apply: bool = False) -> AsyncIterator[Event]
```

`mode` 只能是：

- `diagnosis`
- `repair`

不要改成 `diagnose`。

调用语义：

- 前端只依赖 `BackendController` 和 `event_to_dict` / `event_to_json`。
- 前端不要直接调用内部 `ShellTool` / `PatchPlanner` / `PatchApplier` / `DiagnosisBenchmarkRunner` / `RepairBenchmarkRunner`。
- `confirm_apply=False` 只提出修复计划，不 apply patch。
- `confirm_apply=True` 才允许进入 apply + verification 流程。

推荐消费示例：

```python
controller = BackendController()

async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="repair",
    confirm_apply=True,
):
    payload = event_to_dict(event)
    print(payload)
```

M13/M14/M15-M22 均要求不破坏这个 public API。

## 5. Milestone M15-M22 总览

| Milestone | 目标 | 主要新增/修改模块 | 当前行为 | 测试/验收结果 |
|---|---|---|---|---|
| M15 EnvDoctor | 为 `missing_module` / `missing_file` 增加环境/数据诊断建议 | `scicodepilot/doctor/env_doctor.py`，事件 schema，repair runner/suite runner 相关接入 | 对环境/数据问题生成 `EnvRepairPlanCreated`，不自动安装依赖，不创建缺失文件，不走源码 patch | 用户汇报已完成，`env_repair_plan_count=2` |
| M16 Textual reference frontend | 提供参考 Textual 前端 | `scicodepilot/frontend/textual_app.py`，`scripts/run_textual_app.py`，前端 handoff 文档 | 通过 `BackendController.run_task()` 消费事件流，作为参考 UI，不改变后端 API | 用户汇报 smoke test 可用 |
| M17 Optional LLM PatchPlanner | 增加可选 LLM patch planner adapter | `scicodepilot/llm/llm_patch_planner.py` 等 | 默认关闭；失败时 fallback 到 rule-based `PatchPlanner` | 用户汇报已完成 |
| M18 Multi-provider LLM planner | 多 provider LLM planner | `scicodepilot/llm/llm_client.py`、provider 配置、prompt templates | 支持 `mock` / `deepseek` / `gemini` / `openai` / `disabled`；默认关闭 | mock LLM repair 用户汇报 average_score=1.0 |
| M19 PatchSafetyReviewer | 所有 patch 进入 apply 前必须安全审查 | `scicodepilot/review/patch_safety_reviewer.py`、`patch_review.py`、事件 `PatchReviewCreated` | blocked patch 不进入 confirmation/apply/hidden evaluator | safety stress cases 用户汇报 10 passed |
| M20 Research Evaluation Pack | 增加研究评测脚本与报告资产 | `scripts/run_experiments.py`、`export_results_table.py`、docs/research docs、outputs/experiments | 可生成实验 summary 和 results table | 用户汇报已完成 |
| M21 Benchmark Expansion 10 tasks | benchmark 从 6 个扩展到 10 个任务 | `benchmark/tasks/*`，parser/memory/planner/test 扩展 | 8 个 source-code repair，2 个 env/data diagnosis | diagnosis suite 用户汇报 10/10 passed |
| M22 Ablation Experiments and Result Analysis | 增加消融实验与结果分析 | `scripts/run_ablation_experiments.py`、`export_ablation_tables.py`、docs/ablation/results | 输出 ablation summary/table/safety table/report assets | 用户汇报已完成 |

## 6. 当前 Benchmark Tasks

当前共有 10 个 controlled benchmark tasks。

| task_id | error_type | category | expected handling module | expected original bug marker |
|---|---|---|---|---|
| `repair_tensor_shape_001` | `tensor_shape` | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `classifier_expected_dim = 128` |
| `repair_dtype_mismatch_002` | `dtype_mismatch` | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `dtype=torch.float64` |
| `repair_missing_module_003` | `missing_module` | env/data diagnosis | `EnvDoctor` | `import definitely_missing_scicodepilot_dependency` |
| `repair_missing_file_004` | `missing_file` | env/data diagnosis | `EnvDoctor` | missing data/config path such as `data/train.csv` or `configs/dataset.json` |
| `repair_entrypoint_error_005` | `entrypoint_error` | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `mainn()` |
| `repair_label_shape_006` | `label_shape` | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `batch_size + 1` |
| `repair_device_mismatch_007` | `device_mismatch` | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `input_device = "cuda:0"` |
| `repair_loss_input_008` | loss/input related error | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `target_kind = "probabilities"` |
| `repair_collate_fn_009` | collate/data structure related error | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `return {"features": xs, "labels": ys}` |
| `repair_config_key_010` | config key related error | source-code repair | `PatchPlanner` -> `PatchSafetyReviewer` -> workspace apply | `config["learningrate"]` |

任务行为总结：

- 8 个 source-code repair tasks 会产生 `PatchPlan` / `PatchReviewCreated` / `PatchApplied` / `score.json`。
- 2 个 env/data diagnosis tasks，即 `repair_missing_module_003` 与 `repair_missing_file_004`，会产生 `EnvRepairPlanCreated`，不产生源码 patch。
- `repair --confirm-apply` 后，8 个 source-code tasks 预期 `verification_success=True` 且 `score=1.0`。
- 所有修复必须发生在 workspace copy 中，原始 benchmark repo 不能被污染。

> 注意：`repair_loss_input_008` / `repair_collate_fn_009` / `repair_config_key_010` 的精确 `error_type` 建议下一位 Codex 以 `reference/expected_diagnosis.json` 为准复核。

## 7. 关键代码目录与模块职责

### `scicodepilot/backend/`

- `controller.py`：前端和外部调用方唯一推荐入口。提供 `list_tasks()`、`get_task()`、`run_task(...)`。
- `event_serializer.py`：将 Pydantic event 转成 dict / JSON，供 Textual 或未来 WebSocket wrapper 使用。
- `frontend_contract.md`：M12 前端接口契约文档，说明事件消费方式和 UI 映射。

### `scicodepilot/events/`

- `schema.py`：所有事件模型与 `Event` 联合类型。M15-M22 之后应包含 diagnosis、repair、env doctor、patch review、verification 等事件。
- `bus.py`：同进程 `asyncio.Queue` 事件总线，最小单消费者/生产者模型。

### `scicodepilot/tools/`

- `shell_tool.py`：异步执行命令，实时捕获 stdout/stderr，发出 `CommandStarted` / `CommandOutput` / `CommandFinished`，返回 `CommandResult`。
- `command_result.py`：命令完成后的汇总结果，保存 return code、stdout/stderr lines。
- `traceback_parser.py`：规则表 parser，从 stderr 中识别 `tensor_shape`、`dtype_mismatch`、`missing_module`、`missing_file`、`entrypoint_error`、`label_shape`、`device_mismatch` 等错误类型。

### `scicodepilot/memory/`

- `failure_memory.py`：`FailureMemory` 数据模型与 `FailureMemoryBuilder`。把 `ParsedError` 转成结构化 root cause hypothesis 和 repair action。

### `scicodepilot/repair/`

- `patch_plan.py`：`PatchPlan` 结构化修复计划。
- `patch_planner.py`：确定性 rule-based planner，benchmark 主路径。针对当前 controlled tasks 生成 unified diff。
- `patch_applier.py`：最小单文件文本替换式 applier；只在 workspace repo 中使用。
- `repair_policy.py`：确认边界，`require_confirmation` / `approved` / `can_apply_patch()`。
- `repair_result.py`：repair workflow 返回结果，包含 patch、verification、score 等状态。
- `repair_runner.py`：repair workflow 编排器。M14 后应先创建 workspace，再运行诊断、env doctor 或 patch planner、安全审查、确认、apply、verification、hidden evaluator。

### `scicodepilot/review/`

- `patch_review.py`：Patch review 数据模型。
- `patch_safety_reviewer.py`：静态安全审查器。所有 `PatchPlan` 必须先通过 reviewer。

### `scicodepilot/eval/`

- `task_loader.py`：加载 benchmark metadata，生成 `BenchmarkTask`。
- `diagnosis_evaluator.py`：根据 expected diagnosis 判断诊断是否通过。
- `diagnosis_runner.py`：diagnosis-only runner。
- `suite_result.py`：suite case result 和 summary model。
- `suite_runner.py`：批量运行 diagnosis / repair suite，生成 summary 计数。
- `workspace.py`：`WorkspaceManager`，将 task repo 复制到 `outputs/workspaces/<run_id>/<task_id>/repo`。
- `score_result.py`：hidden evaluator score model。
- `hidden_evaluator.py`：在 workspace repo 运行 verification command，生成 `score.json`。

### `scicodepilot/llm/`

- `llm_client.py`：LLM provider client 抽象/选择逻辑。
- `llm_patch_planner.py`：optional LLM patch planner adapter。
- `prompt_templates.py`：LLM planner prompt 模板。
- `README.md`：LLM planner 使用说明和 provider 配置。

### `scicodepilot/frontend/`

- `textual_app.py`：M16 Textual reference frontend，作为事件流消费示例，不是核心后端 API。

### `scripts/`

- `run_benchmark_suite.py`：批量运行 benchmark suite，输出 `results.jsonl` / `summary.json`。
- `run_frontend_contract_demo.py`：模拟前端消费 `BackendController` 事件流。
- `run_textual_app.py`：运行 Textual reference frontend，可用 `--smoke-test` 做轻量验证。
- `run_showcase.py`：showcase/demo 脚本。
- `run_experiments.py`：M20 research experiment pack 主入口。
- `export_results_table.py`：导出实验结果表。
- `run_ablation_experiments.py`：M22 ablation runner。
- `export_ablation_tables.py`：导出消融和 safety 表。

### `docs/`

- `research_questions.md`：研究问题。
- `experiment_protocol.md`：实验协议。
- `failure_taxonomy.md`：失败类型分类。
- `safety_cases.md`：安全案例。
- `ablation_study.md`：消融研究说明。
- `results_analysis.md`：结果分析。
- `final_status.md`：当前阶段状态。
- `architecture.md`：架构说明。
- `demo_guide.md`：demo 指南。
- `frontend_handoff_checklist.md`：如果存在，是给前端同学的交接清单。
- `CODEX_HANDOFF_M1_M14.md`：M1-M14 交接文档。
- `CODEX_HANDOFF_M15_M22.md`：本文档。

### `tests/`

测试大致覆盖：

- event schema / serializer / backend controller public API
- traceback parser / failure memory / EnvDoctor
- PatchPlanner / PatchApplier / RepairPolicy / RepairBenchmarkRunner
- PatchSafetyReviewer 和 safety stress cases
- workspace copy / hidden evaluator / score.json
- suite runner diagnosis/repair summary
- LLM mock planner / fallback
- Textual smoke / research scripts / ablation outputs

## 8. Event Schema 和事件流

当前重要事件类型如下。

| Event | 触发时机 | 主要字段 | UI / report 含义 |
|---|---|---|---|
| `TaskStarted` | task workflow 开始 | `task_id`, `task_name` | 页面标题、任务状态起点 |
| `PlanCreated` | runner 创建执行计划 | `steps` | plan tree / step list |
| `StepStarted` | 每个阶段开始 | `step_index`, `step_name` | 当前 active step |
| `CommandStarted` | ShellTool 启动命令 | `command` | log panel command header |
| `CommandOutput` | stdout/stderr 每行输出 | `stream`, `content` | terminal/log panel，stderr 高亮 |
| `CommandFinished` | 命令结束 | `return_code`, `success` | command status |
| `ErrorDetected` | parser 识别错误 | `error_type`, `summary`, `evidence` | error card |
| `FailureMemoryCreated` | failure memory 生成 | `root_cause_hypothesis`, `repair_action` | reflection/memory card |
| `EnvRepairPlanCreated` | EnvDoctor 生成环境/数据修复建议 | issue/advice/user action 字段 | env/data issue card |
| `PatchProposed` | PatchPlan 生成 | `target_file`, `confidence`, `unified_diff` | diff panel |
| `PatchReviewCreated` | PatchSafetyReviewer 完成审查 | review status/reasons | safety review card |
| `PatchApprovalRequired` | `confirm_apply=False` 且 patch 可审查通过 | `target_file`, `unified_diff` | permission prompt |
| `PatchApplied` | patch apply 被尝试 | `success`, `target_file`, `message` | patch status |
| `VerificationStarted` | apply 后开始验证 | `command`, `cwd` | verification status |
| `VerificationFinished` | 验证命令完成 | `return_code`, `success`, `summary` | verification result |
| `TaskFinished` | 整个 workflow 结束 | `status`, `summary` | final status |

说明：

- 所有事件都应能经过 `event_to_dict` / `event_to_json` 转换给前端。
- `EnvRepairPlanCreated` 是 env/data issue card，不是 patch card。
- `PatchReviewCreated` 是 safety review card，是 patch apply 前的必经节点。
- `PatchApprovalRequired` 只在 repair `confirm_apply=False` 且 patch 未被 blocked 时出现。
- blocked patch 不进入 `PatchApprovalRequired` / `PatchApplied` / hidden evaluator。

## 9. EnvDoctor 设计

EnvDoctor 专门处理不适合源码自动 patch 的环境/数据类问题。

- `missing_module` -> dependency issue。
- `missing_file` -> data/config issue。
- 只生成 `EnvRepairPlanCreated`。
- 不自动 `pip install`。
- 不自动 `conda install`。
- 不自动创建缺失文件。
- 如果模型中存在 `requires_user_action=True`，它表示该问题需要用户在环境、依赖、数据下载或路径配置层面手动处理。

M15 之后，`repair_missing_module_003` 和 `repair_missing_file_004` 应保持 diagnosis/env-plan only，不应由 PatchPlanner 强行修源码。

## 10. PatchSafetyReviewer 设计

`PatchSafetyReviewer` 是 M19 的安全边界。

核心规则：

- 所有 `PatchPlan` 都必须经过 reviewer。
- reviewer 不执行 shell，不修改文件。
- blocked patch 不进入 confirmation/apply。
- blocked patch 不进入 hidden evaluator。
- 不允许为了提高结果绕过 reviewer。

当前应拦截或标记的风险包括：

- absolute path
- `../` path traversal
- workspace 外路径
- `benchmark/`
- `reference/`
- `outputs/`
- `tests/`
- `.git/`
- `pyproject.toml`
- `requirements.txt`
- multi-file dangerous diff
- `rm -rf`
- `sudo`
- `pip install`
- `conda install`
- `os.system`
- `subprocess`
- `eval`
- `exec`

用户汇报：safety stress cases 当前 10 passed。

## 11. LLM Planner 状态

LLM planner 是 optional，不是默认路径。

当前语义：

- 默认关闭。
- deterministic rule-based `PatchPlanner` 是 benchmark 主路径。
- 支持 provider：
  - `mock`
  - `deepseek`
  - `gemini`
  - `openai`
  - `disabled`
- 关键环境变量：
  - `SCICODEPILOT_LLM_PROVIDER`
  - `SCICODEPILOT_DEEPSEEK_API_KEY`
  - `SCICODEPILOT_GEMINI_API_KEY`
  - `SCICODEPILOT_OPENAI_API_KEY`

注意：

- ChatGPT Pro 不等于 OpenAI API key。
- 真实 provider 尚未系统性评测。
- LLM 失败必须 fallback 到 rule-based planner。
- LLM 生成的 patch 仍必须经过 `PatchSafetyReviewer`。
- 不要把 LLM planner 改成默认开启。

## 12. Research Evaluation Pack / Ablation Pack

M20-M22 增加了研究评测、表格导出、消融实验和报告资产。

核心脚本：

- `scripts/run_experiments.py`
- `scripts/export_results_table.py`
- `scripts/run_ablation_experiments.py`
- `scripts/export_ablation_tables.py`

输出目录：

- `outputs/experiments/...`
- `outputs/ablations/...`
- `report_assets/tables/...`

已知输出路径：

- `outputs/experiments/20260522_194640/summary.json`
- `outputs/experiments/20260522_194640/results_table.md`
- `outputs/ablations/20260522_195640/ablation_summary.json`
- `outputs/ablations/20260522_195640/ablation_table.md`
- `outputs/ablations/20260522_195640/safety_table.md`
- `report_assets/tables/ablation_table.md`
- `report_assets/tables/safety_table.md`

这些产物用于内部报告和后续公开 benchmark 接入前的 sanity / ablation / safety 分析。

## 13. 当前验证命令与期望结果

进入项目：

```bash
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
```

跑全部测试：

```bash
pytest -q
```

跑 diagnosis suite：

```bash
python scripts/run_benchmark_suite.py --mode diagnosis
```

跑 repair suite，不实际 apply：

```bash
python scripts/run_benchmark_suite.py --mode repair
```

跑 repair suite，确认 apply：

```bash
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

跑 mock LLM repair：

```bash
SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

跑 research experiments：

```bash
python scripts/run_experiments.py --quick
python scripts/export_results_table.py --latest
```

跑 ablation experiments：

```bash
python scripts/run_ablation_experiments.py --quick --include-safety
python scripts/export_ablation_tables.py --latest
```

跑 Textual smoke test：

```bash
python scripts/run_textual_app.py --smoke-test
```

用户汇报的当前期望结果：

- `pytest -q`: `136 passed`
- diagnosis suite: `total_tasks=10`, `diagnosis_pass_count=10`
- repair without apply: `patch_plan_count=8`, `patch_review_count=8`, `patch_applied_count=0`, `env_repair_plan_count=2`
- repair `--confirm-apply`: `patch_review_count=8`, `patch_review_blocked_count=0`, `patch_applied_count=8`, `verification_success_count=8`, `scored_task_count=8`, `env_repair_plan_count=2`, `average_score=1.0`
- mock LLM repair: `patch_review_count=8`, `patch_review_blocked_count=0`, `average_score=1.0`
- safety stress cases: `10 passed`

本轮生成 handoff 时未能通过 WSL 重新运行这些命令，下一位 Codex 接手后应先复验。

## 14. 原始 Benchmark 污染检查

以下 grep 命令用于确认原始 benchmark bug 没有被 workspace repair 污染：

```bash
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py
grep 'input_device = "cuda:0"' benchmark/tasks/repair_device_mismatch_007/repo/train.py
grep 'target_kind = "probabilities"' benchmark/tasks/repair_loss_input_008/repo/train.py
grep 'return {"features": xs, "labels": ys}' benchmark/tasks/repair_collate_fn_009/repo/train.py
grep 'config\["learningrate"\]' benchmark/tasks/repair_config_key_010/repo/train.py
```

这些原始 bug marker 必须仍然存在：

- `classifier_expected_dim = 128`
- `dtype=torch.float64`
- `mainn()`
- `batch_size + 1`
- `input_device = "cuda:0"`
- `target_kind = "probabilities"`
- `return {"features": xs, "labels": ys}`
- `config["learningrate"]`

`repair_missing_module_003` 与 `repair_missing_file_004` 也应保持原始缺依赖/缺文件状态，因为它们是 EnvDoctor diagnosis-only tasks。

## 15. 当前已知限制

- 当前内部 benchmark 是 controlled 10-task benchmark，不应夸大为真实大型科研仓库泛化结果。
- hidden evaluator 当前较轻量，主要根据 entry command / `score.json`。
- rule-based `PatchPlanner` 针对当前错误模式设计。
- LLM planner 虽然支持多 provider，但默认关闭，真实 provider 尚未系统评测。
- EnvDoctor 只生成 plan，不自动修环境。
- PatchSafetyReviewer 是静态规则系统，可能 conservative。
- 当前 `average_score=1.0` 只说明当前 10-task benchmark 全部通过，不代表通用 100% 准确率。

## 16. 附件计划中的后续 35 天方向

后续计划核心：

- 冻结方法实现，不改 public API，不继续堆功能。
- 把内部 10-task benchmark 降级为 sanity check。
- 主结论迁移到公开 benchmark + 组件消融 + 安全/失败分析。
- 优先考虑：
  1. BugsInPy：真实 Python bug repair 主线。
  2. SWE-bench Lite scientific-Python 子集：仓库级 issue repair 主线。
  3. DebugBench Python 子集：FailureMemory / diagnosis 对比。
  4. SciCode 或 DS-1000 repair-after-generate：科研代码定位辅助实验。
- 不建议本轮把 MLE-bench / PaperBench 作为主战场。
- 后续新增工作应放在 adapter、config、script、analysis、report_assets 层，不要动核心 public API。
- 需要补：
  - reproducibility bundle
  - public benchmark adapter
  - baseline comparison
  - stage-wise task_score
  - confidence interval
  - paired significance tests
  - failure buckets
  - report figures/tables

## 17. 后续不要做的事

- 不要继续新增内部 benchmark 到失控规模。
- 不要继续堆 LLM provider。
- 不要把 LLM 默认开启。
- 不要关闭 safety reviewer 来追结果。
- 不要在真实 repo 上直接 patch，必须 disposable workspace/container。
- 不要用内部 10-task perfect score 作为泛化结论。
- 不要改 `BackendController` public API。
- 不要把 docs website 做成复杂 dashboard。

## 18. 给下一位 Codex 的建议入口

如果下一位 Codex 接手，优先任务应是：

1. 读取本 handoff。
2. 运行第 13 节验证命令。
3. 生成 reproducibility bundle。
4. 设计 public benchmark adapter，不改核心 API。
5. 接 BugsInPy pilot。
6. 接 DebugBench diagnosis pilot。
7. 再考虑 SWE-bench Lite scientific-Python subset。
8. 产出 `report_assets`，而不是继续堆功能。

建议接手后第一轮只做验证和报告资产，不要修改核心 repair runner、planner、reviewer 或 BackendController public API。
