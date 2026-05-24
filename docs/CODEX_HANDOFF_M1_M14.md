# SciCodePilot M1–M14 Codex 代码仓库级交接文档

本文档是给下一个 Codex/GPT 继续开发 SciCodePilot 后端使用的代码仓库级交接文档。它基于当前仓库真实文件状态、已运行命令结果，以及本轮 M1–M14 的开发历史整理。

项目基本信息：

- 项目名：SciCodePilot
- 项目路径：`/home/zengl/projects/SciCodePilot`
- 运行环境：WSL Ubuntu
- Conda 环境：`scicodepilot-dev`
- 所有项目命令必须在 WSL Ubuntu 中运行，不要在 Windows PowerShell 中运行。
- 涉及 Python / pip 时，优先使用当前 conda 环境中的 `python` / `pip`。

标准进入项目命令：

```bash
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
```

---

## 1. 当前项目状态总览

当前项目已完成 M1–M14。

当前状态：

- benchmark 已扩展到 6 个任务：
  - `repair_tensor_shape_001`
  - `repair_dtype_mismatch_002`
  - `repair_missing_module_003`
  - `repair_missing_file_004`
  - `repair_entrypoint_error_005`
  - `repair_label_shape_006`
- 当前实际运行的 `pytest -q` 结果为：

```text
68 passed in 23.88s
```

注意：用户请求中提到“65 passed”是 M13 后的历史基线；当前仓库 M14 后真实状态是 `68 passed`。

- `BackendController` public API 未改变：
  - `list_tasks()`
  - `get_task(task_id)`
  - `run_task(task_id, mode, confirm_apply=False)`
- M14 已实现 isolated workspace / hidden evaluator / `score.json`。
- repair workflow 已不再污染 `benchmark/tasks/*/repo` 原始任务目录。
- patch/verification/hidden evaluator 均在 workspace repo 中执行。
- 当前 diagnosis-only 的任务：
  - `repair_missing_module_003`
  - `repair_missing_file_004`
- 当前支持自动 patch 的任务：
  - `repair_tensor_shape_001`
  - `repair_dtype_mismatch_002`
  - `repair_entrypoint_error_005`
  - `repair_label_shape_006`
- 下一阶段建议：M15，新增 EnvDoctor，专门处理 `missing_module` / `missing_file`。

---

## 2. M1–M14 里程碑逐项总结

### M1：Event Schema + EventBus + 最小后端 demo

目标：

- 建立同进程 asyncio 事件流。
- 不接 LLM、不接 UI、不真实执行 shell。

实际完成：

- 定义基础事件模型。
- 实现 `EventBus`。
- 实现 `DemoOrchestrator` 手动发出模拟事件。
- 实现 `scripts/run_backend_demo.py` 打印事件流。

创建/修改文件：

- `scicodepilot/events/schema.py`
- `scicodepilot/events/bus.py`
- `scicodepilot/agent/demo_orchestrator.py`
- `scripts/run_backend_demo.py`

新增类/函数/结构：

- `TaskStarted`
- `PlanCreated`
- `StepStarted`
- `CommandStarted`
- `CommandOutput`
- `ErrorDetected`
- `FailureMemoryCreated`
- `TaskFinished`
- `Event`
- `EventBus.emit`
- `EventBus.next_event`
- `EventBus.queue_size`

关键命令：

```bash
python scripts/run_backend_demo.py
```

测试/验证：

- 初期手动验证 demo 输出事件顺序正确。

已知风险/踩坑：

- 最早在 Windows PowerShell 环境运行时缺少 `pydantic`，后来明确所有命令必须在 WSL Ubuntu + conda 环境中执行。

### M2：真实异步 ShellTool

目标：

- 将手动伪造 CommandOutput 升级为真实异步执行脚本。
- 实时捕获 stdout/stderr。
- 命令结束发出 `CommandFinished`。

实际完成：

- 新增 `ShellTool`。
- 新增 `scripts/mock_training_error.py`。
- `DemoOrchestrator` 改为调用 `ShellTool.run(...)`。

创建/修改文件：

- `scicodepilot/tools/shell_tool.py`
- `scripts/mock_training_error.py`
- `scicodepilot/events/schema.py`
- `scicodepilot/agent/demo_orchestrator.py`
- `scripts/run_backend_demo.py`

新增事件：

- `CommandFinished`

关键逻辑：

- `asyncio.create_subprocess_shell(...)`
- 并发读取 stdout/stderr。
- 每行输出转成 `CommandOutput`。

关键命令：

```bash
python scripts/run_backend_demo.py
```

测试/验证：

- 手动验证 `return_code=1`、stderr 单独标识、程序不阻塞。

风险/踩坑：

- 必须并发读 stdout/stderr，不能顺序读，避免潜在阻塞。

### M3：CommandResult + TracebackParser + FailureMemoryBuilder

目标：

- `ErrorDetected` 和 `FailureMemoryCreated` 不再由 orchestrator 手写。
- 从真实 stderr 中自动解析、自动生成。

实际完成：

- 新增 `CommandResult`。
- `ShellTool.run(...)` 返回 `CommandResult`。
- 新增 `TracebackParser`，初始识别 `tensor_shape`。
- 新增/实现 `FailureMemory` 和 `FailureMemoryBuilder`。
- `DemoOrchestrator` 改为 parser + builder 自动诊断。

创建/修改文件：

- `scicodepilot/tools/command_result.py`
- `scicodepilot/tools/traceback_parser.py`
- `scicodepilot/memory/failure_memory.py`
- `scicodepilot/tools/shell_tool.py`
- `scicodepilot/agent/demo_orchestrator.py`

新增类：

- `CommandResult`
- `ParsedError`
- `TracebackParser`
- `FailureMemory`
- `FailureMemoryBuilder`

关键命令：

```bash
python scripts/run_backend_demo.py
```

测试/验证：

- 手动验证 `tensor_shape` 由 parser 产生，failure memory 由 builder 产生。

风险/踩坑：

- `CommandOutput` 是流式事件，`CommandResult` 是命令完成后的汇总结果；两者职责要分清。

### M4：规则表 Parser + 多错误类型 + 单元测试

目标：

- 将 parser 从单条硬编码 if 升级为规则表。
- 支持多种错误类型。
- 补核心模块单元测试。

实际完成：

- `TracebackParser` 增加 `ErrorRule` / `ERROR_RULES`。
- 支持：
  - `tensor_shape`
  - `device_mismatch`
  - `dtype_mismatch`
  - `missing_module`
- `FailureMemoryBuilder` 支持 4 类错误。
- 新增测试。

创建/修改文件：

- `scicodepilot/tools/traceback_parser.py`
- `scicodepilot/memory/failure_memory.py`
- `tests/test_traceback_parser.py`
- `tests/test_failure_memory.py`
- `tests/test_shell_tool.py`

新增结构：

- `ErrorRule`
- `ERROR_RULES`

关键命令：

```bash
pytest -q
python scripts/run_backend_demo.py
```

测试结果：

- 当时测试为 `11 passed`。

风险/踩坑：

- `pytest` 一开始无法 import `scicodepilot`，测试文件中加入了最小项目根路径处理。

### M5：第一个 benchmark diagnosis-only 任务

目标：

- 引入 `repair_tensor_shape_001` benchmark。
- 实现 diagnosis-only 闭环。
- 输出 benchmark diagnosis summary。

实际完成：

- 新增 benchmark 目录：
  - `benchmark/tasks/repair_tensor_shape_001`
- 新增 eval 模块：
  - task loader
  - diagnosis evaluator
  - diagnosis runner
- `ShellTool.run(...)` 支持 `cwd`。
- 新增 `scripts/run_benchmark_diagnosis_demo.py`。

创建/修改文件：

- `benchmark/tasks/repair_tensor_shape_001/task.md`
- `benchmark/tasks/repair_tensor_shape_001/metadata.json`
- `benchmark/tasks/repair_tensor_shape_001/repo/train.py`
- `benchmark/tasks/repair_tensor_shape_001/reference/expected_diagnosis.json`
- `scicodepilot/eval/task_loader.py`
- `scicodepilot/eval/diagnosis_evaluator.py`
- `scicodepilot/eval/diagnosis_runner.py`
- `scripts/run_benchmark_diagnosis_demo.py`
- `tests/test_task_loader.py`
- `tests/test_diagnosis_evaluator.py`

新增类/函数：

- `BenchmarkTask`
- `load_benchmark_task`
- `ExpectedDiagnosis`
- `DiagnosisEvaluationResult`
- `load_expected_diagnosis`
- `evaluate_diagnosis`
- `DiagnosisRunResult`
- `DiagnosisBenchmarkRunner`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_diagnosis_demo.py
```

测试结果：

- 当时测试增长到 `15 passed`。

风险/踩坑：

- benchmark command 必须在 task `repo/` 下运行，因此 `ShellTool` 增加了 `cwd`。

### M6：真实轻量 PyTorch shape bug

目标：

- 将 `repair_tensor_shape_001` 从手写 stderr 模拟升级为真实 PyTorch CPU shape bug。

实际完成：

- `train.py` 改为真实 PyTorch 脚本。
- 明确使用 `torch.device("cpu")`。
- metadata 增加 `requires: ["torch"]`。
- `BenchmarkTask` 增加 `requires` 字段。
- 新增测试用 `pytest.importorskip("torch")`。

创建/修改文件：

- `benchmark/tasks/repair_tensor_shape_001/task.md`
- `benchmark/tasks/repair_tensor_shape_001/metadata.json`
- `benchmark/tasks/repair_tensor_shape_001/repo/train.py`
- `scicodepilot/eval/task_loader.py`
- `tests/test_task_loader.py`
- `tests/test_repair_tensor_shape_task.py`

新增/修改结构：

- `BenchmarkTask.requires: list[str] = Field(default_factory=list)`

关键命令：

```bash
python -c "import torch; print(torch.__version__)"
pytest -q
python scripts/run_benchmark_diagnosis_demo.py
```

测试/验证：

- 中途环境曾出现 `ModuleNotFoundError: No module named 'torch'`；之后环境中 torch 可用，真实 PyTorch task 测试通过。

风险/踩坑：

- 不允许写 CUDA，不要求 GPU。
- 不允许手写 RuntimeError，要让 PyTorch 自己抛真实 traceback。

### M7：PatchPlan

目标：

- 实现自动修复前的 Patch Plan。
- 不真正修改文件。
- 输出 unified diff 草案。

实际完成：

- 新增 repair 层。
- 定义 `PatchPlan`。
- 实现 `PatchPlanner`，初始支持 `tensor_shape`。
- `DiagnosisRunResult` 增加 `patch_plan`。
- benchmark diagnosis demo 显示 Patch Plan。

创建/修改文件：

- `scicodepilot/repair/__init__.py`
- `scicodepilot/repair/patch_plan.py`
- `scicodepilot/repair/patch_planner.py`
- `scicodepilot/eval/diagnosis_runner.py`
- `scripts/run_benchmark_diagnosis_demo.py`
- `tests/test_patch_planner.py`

新增类：

- `PatchPlan`
- `PatchPlanner`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_diagnosis_demo.py
```

测试结果：

- 当时测试为 `19 passed`。

风险/踩坑：

- diff 必须由 `difflib.unified_diff` 生成。
- M7 不允许 apply patch。

### M8：PatchApplier + RepairResult + Repair Demo

目标：

- 实现“手动确认后 apply patch”的最小安全修复流程。
- 应用 M7 生成的 diff。
- 重新运行 benchmark command 验证。
- 结束后恢复原始 bug。

实际完成：

- 新增 `PatchApplier`。
- 新增 `RepairResult`。
- 新增 `scripts/run_benchmark_repair_demo.py`。
- 初版 repair demo 在原始 repo 中临时 apply，并 finally 恢复。

创建/修改文件：

- `scicodepilot/repair/repair_result.py`
- `scicodepilot/repair/patch_applier.py`
- `scripts/run_benchmark_repair_demo.py`
- `tests/test_patch_applier.py`
- `scicodepilot/repair/__init__.py`

新增类：

- `PatchApplier`
- `RepairResult`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_repair_demo.py
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
```

测试结果：

- 当时测试为 `23 passed`。

风险/踩坑：

- `PatchApplier` 不是通用 patch 引擎，仅支持简单单文件 old/new 行替换。
- M8 还会临时修改原始 benchmark repo，M14 已修复此设计。

### M9：Repair workflow 事件流

目标：

- 把 M8 repair demo 接入 EventBus。
- 新增 repair 相关事件。

实际完成：

- 新增事件：
  - `PatchApplied`
  - `VerificationStarted`
  - `VerificationFinished`
- 新增 `RepairBenchmarkRunner`。
- repair demo 改为使用 runner。
- repair workflow 只在整体结束时 emit 一个 `TaskFinished`。

创建/修改文件：

- `scicodepilot/events/schema.py`
- `scicodepilot/repair/repair_runner.py`
- `scripts/run_benchmark_repair_demo.py`
- `tests/test_repair_events.py`
- `tests/test_repair_runner.py`

新增类/事件：

- `RepairBenchmarkRunner`
- `PatchApplied`
- `VerificationStarted`
- `VerificationFinished`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_repair_demo.py
```

测试结果：

- 当时测试为 `27 passed`。

风险/踩坑：

- 不要调用 `DiagnosisBenchmarkRunner` 再进入 repair，否则诊断阶段会提前发 `TaskFinished`。

### M10：确认边界 / 权限控制

目标：

- 默认只提出 patch plan，不 apply。
- 显式确认后才 apply + verification。

实际完成：

- 新增 `RepairPolicy`。
- 新增事件：
  - `PatchProposed`
  - `PatchApprovalRequired`
- `RepairBenchmarkRunner.run(task, policy=None)` 默认 `RepairPolicy(require_confirmation=True, approved=False)`。
- `run_benchmark_repair_demo.py` 新增 `--confirm-apply`。

创建/修改文件：

- `scicodepilot/repair/repair_policy.py`
- `scicodepilot/events/schema.py`
- `scicodepilot/repair/repair_result.py`
- `scicodepilot/repair/repair_runner.py`
- `scripts/run_benchmark_repair_demo.py`
- `tests/test_repair_policy.py`
- `tests/test_repair_events.py`
- `tests/test_repair_runner.py`

新增类/事件：

- `RepairPolicy`
- `PatchProposed`
- `PatchApprovalRequired`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_repair_demo.py
python scripts/run_benchmark_repair_demo.py --confirm-apply
```

测试结果：

- 当时测试为 `34 passed`。

风险/踩坑：

- 默认 repair 不能 apply patch。
- 只有 `confirm_apply=True` 或 `RepairPolicy(require_confirmation=False)` 才能 apply。

### M11：多任务 benchmark suite

目标：

- benchmark 扩展到多个任务。
- 新增 suite runner。
- 输出 `results.jsonl` 和 `summary.json`。

实际完成：

- 新增两个任务：
  - `repair_dtype_mismatch_002`
  - `repair_missing_module_003`
- 后续 M13 又扩展到 6 个任务。
- 新增 suite result / suite runner / suite script。
- `PatchPlanner` 支持 dtype mismatch。

创建/修改文件：

- `benchmark/tasks/repair_dtype_mismatch_002/*`
- `benchmark/tasks/repair_missing_module_003/*`
- `scicodepilot/eval/suite_result.py`
- `scicodepilot/eval/suite_runner.py`
- `scripts/run_benchmark_suite.py`
- `scicodepilot/repair/patch_planner.py`
- `scicodepilot/tools/traceback_parser.py`
- `tests/test_benchmark_tasks.py`
- `tests/test_suite_runner.py`

新增类/函数：

- `BenchmarkCaseResult`
- `BenchmarkSuiteSummary`
- `BenchmarkSuiteRunner`
- `summarize_results`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_suite.py --mode diagnosis
python scripts/run_benchmark_suite.py --mode repair
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

测试/验证：

- M11 当时 3 任务 suite 正常。

风险/踩坑：

- `mode` 只能是 `diagnosis` / `repair`，不要写成 `diagnose`。

### M12：BackendController + frontend contract

目标：

- 为未来 Textual 前端提供稳定后端接口。
- 不实现 UI。

实际完成：

- 新增 `scicodepilot/backend/`。
- 新增 `BackendController`。
- 新增 event serializer。
- 新增 `frontend_contract.md`。
- 新增 fake frontend consumer demo。

创建/修改文件：

- `scicodepilot/backend/__init__.py`
- `scicodepilot/backend/controller.py`
- `scicodepilot/backend/event_serializer.py`
- `scicodepilot/backend/frontend_contract.md`
- `scripts/run_frontend_contract_demo.py`
- `tests/test_backend_controller.py`
- `tests/test_event_serializer.py`

新增类/函数：

- `TaskInfo`
- `BackendController`
- `event_to_dict`
- `event_to_json`

关键命令：

```bash
pytest -q
python scripts/run_frontend_contract_demo.py
python scripts/run_frontend_contract_demo.py --task-id repair_missing_module_003 --mode diagnosis
python scripts/run_frontend_contract_demo.py --task-id repair_tensor_shape_001 --mode repair --confirm-apply
```

测试结果：

- 当时测试为 `51 passed`。

风险/踩坑：

- 前端只应依赖 `BackendController` 和 `event_serializer`，不要直接依赖内部 runner/tool。

### M13：扩展 benchmark 到 6 个任务

目标：

- 新增 3 个 benchmark tasks。
- 扩展诊断与 patch 规则。

实际完成：

- 新增：
  - `repair_missing_file_004`
  - `repair_entrypoint_error_005`
  - `repair_label_shape_006`
- `TracebackParser` 支持：
  - `missing_file`
  - `entrypoint_error`
  - `label_shape`
- `FailureMemoryBuilder` 支持新错误类型。
- `PatchPlanner` 支持：
  - `entrypoint_error`: `mainn()` -> `main()`
  - `label_shape`: `(batch_size + 1,)` -> `(batch_size,)`
- `missing_module` / `missing_file` 保持 diagnosis-only。

创建/修改文件：

- `benchmark/tasks/repair_missing_file_004/*`
- `benchmark/tasks/repair_entrypoint_error_005/*`
- `benchmark/tasks/repair_label_shape_006/*`
- `scicodepilot/tools/traceback_parser.py`
- `scicodepilot/memory/failure_memory.py`
- `scicodepilot/repair/patch_planner.py`
- `tests/test_traceback_parser.py`
- `tests/test_failure_memory.py`
- `tests/test_patch_planner.py`
- `tests/test_benchmark_tasks.py`
- `tests/test_suite_runner.py`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_suite.py --mode diagnosis
python scripts/run_benchmark_suite.py --mode repair
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

测试结果：

- M13 后测试为 `65 passed`。

风险/踩坑：

- 没有 `repair_device_mismatch_002`；真实仓库中当前是 `repair_dtype_mismatch_002`。
- 新任务命名已固定为当前 6 个任务，无旧命名待清理。

### M14：Hidden Evaluator / Workspace Copy / score.json

目标：

- repair/evaluation 在 isolated workspace 中执行。
- 不再临时修改 benchmark 原始 repo。
- 生成 `score.json`。

实际完成：

- 新增 `WorkspaceManager` / `WorkspaceInfo`。
- 新增 `ScoreResult`。
- 新增 `HiddenEvaluator`。
- `RepairBenchmarkRunner` 改为先复制 workspace，再在 workspace repo 中运行 original command / patch / verification / hidden evaluator。
- suite result 和 summary 增加 score/workspace 字段。

创建/修改文件：

- `scicodepilot/eval/workspace.py`
- `scicodepilot/eval/score_result.py`
- `scicodepilot/eval/hidden_evaluator.py`
- `scicodepilot/repair/repair_runner.py`
- `scicodepilot/repair/repair_result.py`
- `scicodepilot/eval/suite_result.py`
- `scicodepilot/eval/suite_runner.py`
- `scripts/run_benchmark_suite.py`
- `tests/test_workspace.py`
- `tests/test_hidden_evaluator.py`
- `tests/test_repair_runner.py`
- `tests/test_suite_runner.py`

关键命令：

```bash
pytest -q
python scripts/run_benchmark_suite.py --mode diagnosis
python scripts/run_benchmark_suite.py --mode repair
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

测试结果：

- 当前实际测试为 `68 passed`。

风险/踩坑：

- `HiddenEvaluator` 当前只是最小 evaluator，仅基于 `entry_command` return code 评分。
- `score.json` 不是复杂 hidden tests 的结果，未来可扩展。

---

## 3. 当前仓库结构与核心文件职责

### `scicodepilot/`

后端主包。

### `scicodepilot/backend/`

前端推荐调用入口。

- `controller.py`
  - 定义 `TaskInfo`
  - 定义 `BackendController`
  - 提供 `list_tasks()` / `get_task()` / `run_task(...)`
- `event_serializer.py`
  - `event_to_dict(event)`
  - `event_to_json(event)`
  - 负责将 Pydantic event 转成前端可消费 dict/json。
- `frontend_contract.md`
  - 给前端同学看的接口约定。
- `__init__.py`
  - 导出 public API。

### `scicodepilot/events/`

事件模型和事件总线。

- `schema.py`
  - 定义全部事件 Pydantic 模型。
  - 定义 `Event` union。
- `bus.py`
  - `EventBus`
  - 基于 `asyncio.Queue[Event]`
  - 当前是同进程单队列事件流，不是多订阅者 pub-sub。

### `scicodepilot/tools/`

底层工具。

- `shell_tool.py`
  - 异步执行 shell command。
  - 实时发 `CommandStarted` / `CommandOutput` / `CommandFinished`。
  - 返回 `CommandResult`。
  - 支持 `cwd`。
- `command_result.py`
  - 命令完成后的 stdout/stderr/return_code 汇总。
- `traceback_parser.py`
  - 规则表 parser。
  - 当前识别：
    - `tensor_shape`
    - `device_mismatch`
    - `dtype_mismatch`
    - `missing_module`
    - `missing_file`
    - `entrypoint_error`
    - `label_shape`

### `scicodepilot/memory/`

失败记忆。

- `failure_memory.py`
  - `FailureMemory`
  - `FailureMemoryBuilder`
  - 根据 `ParsedError.error_type` 生成 root cause hypothesis 和 repair action。

### `scicodepilot/repair/`

patch plan / patch apply / repair workflow。

- `patch_plan.py`
  - `PatchPlan`
- `patch_planner.py`
  - 读取 repo 中 `train.py`。
  - 根据 error_type 生成 unified diff 草案。
  - 支持 tensor shape / dtype mismatch / entrypoint / label shape。
  - missing_module / missing_file 返回 None。
- `patch_applier.py`
  - 最小单文件文本替换 applier。
  - 不调用 shell patch，不调用 git apply。
- `repair_policy.py`
  - `RepairPolicy(require_confirmation=True, approved=False)`
  - 控制是否允许 apply。
- `repair_result.py`
  - `RepairResult`
  - 包含 patch、verification、score、workspace 结果。
- `repair_runner.py`
  - `RepairBenchmarkRunner`
  - 负责完整 repair workflow。
  - M14 后使用 workspace repo，不修改原始 benchmark repo。

### `scicodepilot/eval/`

benchmark 评测、suite、workspace、score。

- `task_loader.py`
  - `BenchmarkTask`
  - `load_benchmark_task(...)`
- `diagnosis_evaluator.py`
  - 读取 expected diagnosis。
  - 检查 error type / summary keywords / root cause keywords / repair action keywords。
- `diagnosis_runner.py`
  - diagnosis-only 单任务 runner。
- `suite_result.py`
  - `BenchmarkCaseResult`
  - `BenchmarkSuiteSummary`
- `suite_runner.py`
  - `BenchmarkSuiteRunner`
  - 批量运行 diagnosis/repair。
- `workspace.py`
  - `WorkspaceManager`
  - `WorkspaceInfo`
- `score_result.py`
  - `ScoreResult`
- `hidden_evaluator.py`
  - `HiddenEvaluator`
  - 在 workspace repo 下运行 command 并写 `score.json`。

### `benchmark/` 和 `benchmark/tasks/`

benchmark 任务根目录。当前 6 个任务，每个任务一般包含：

- `task.md`
- `metadata.json`
- `repo/train.py`
- `reference/expected_diagnosis.json`

### `scripts/`

可直接运行的 demo 和 suite 脚本。

- `run_backend_demo.py`
- `run_benchmark_diagnosis_demo.py`
- `run_benchmark_repair_demo.py`
- `run_benchmark_suite.py`
- `run_frontend_contract_demo.py`
- `mock_training_error.py`

### `tests/`

pytest 测试目录。当前实际通过 68 个测试。

### `outputs/`

运行产物目录，如果已运行 suite/repair，会存在：

- `outputs/benchmark_runs/<timestamp>/results.jsonl`
- `outputs/benchmark_runs/<timestamp>/summary.json`
- `outputs/workspaces/<run_id>/<task_id>/repo`
- `outputs/workspaces/<run_id>/<task_id>/score.json`

---

## 4. 当前 benchmark tasks 状态

### 1. `repair_tensor_shape_001`

- 类别：`runtime_repair_diagnosis`
- 真实错误：PyTorch `RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)`
- expected error_type：`tensor_shape`
- entry_command：`python train.py`
- diagnosis：应通过
- patch plan：支持
- patch apply：支持
- repair `--confirm-apply`：应 `verification_success=True`
- score.json：confirm apply 后应生成
- 原始 bug 标志：

```text
classifier_expected_dim = 128
```

### 2. `repair_dtype_mismatch_002`

- 类别：`runtime_repair_diagnosis`
- 真实错误：PyTorch dtype mismatch，例如 `expected m1 and m2 to have the same dtype`
- expected error_type：`dtype_mismatch`
- entry_command：`python train.py`
- diagnosis：应通过
- patch plan：支持
- patch apply：支持
- repair `--confirm-apply`：应 `verification_success=True`
- score.json：confirm apply 后应生成
- 原始 bug 标志：

```text
dtype=torch.float64
```

### 3. `repair_missing_module_003`

- 类别：`environment_repair_diagnosis`
- 真实错误：`ModuleNotFoundError`
- expected error_type：`missing_module`
- entry_command：`python train.py`
- diagnosis：应通过
- patch plan：不支持
- patch apply：不支持
- repair `--confirm-apply`：不应 verification success，因为没有 patch plan
- score.json：不应生成
- 原始 bug 标志：

```text
import definitely_missing_scicodepilot_dependency
```

### 4. `repair_missing_file_004`

- 类别：`data_repair_diagnosis`
- 真实错误：`FileNotFoundError`
- expected error_type：`missing_file`
- entry_command：`python train.py`
- diagnosis：应通过
- patch plan：不支持
- patch apply：不支持
- repair `--confirm-apply`：不应 verification success，因为没有 patch plan
- score.json：不应生成
- 原始 bug 标志：

```text
data/train.csv
```

### 5. `repair_entrypoint_error_005`

- 类别：`runtime_repair_diagnosis`
- 真实错误：`NameError: name 'mainn' is not defined`
- expected error_type：`entrypoint_error`
- entry_command：`python train.py`
- diagnosis：应通过
- patch plan：支持
- patch apply：支持
- repair `--confirm-apply`：应 `verification_success=True`
- score.json：confirm apply 后应生成
- 原始 bug 标志：

```text
mainn()
```

### 6. `repair_label_shape_006`

- 类别：`runtime_repair_diagnosis`
- 真实错误：PyTorch loss label batch mismatch，例如 `Expected input batch_size (8) to match target batch_size (9)`
- expected error_type：`label_shape`
- entry_command：`python train.py`
- diagnosis：应通过
- patch plan：支持
- patch apply：支持
- repair `--confirm-apply`：应 `verification_success=True`
- score.json：confirm apply 后应生成
- 原始 bug 标志：

```text
batch_size + 1
```

支持自动 patch 的任务：

- `repair_tensor_shape_001`
- `repair_dtype_mismatch_002`
- `repair_entrypoint_error_005`
- `repair_label_shape_006`

diagnosis-only 的任务：

- `repair_missing_module_003`
- `repair_missing_file_004`

---

## 5. 当前事件系统

当前事件类型定义在 `scicodepilot/events/schema.py`。

### `TaskStarted`

- 触发：任务开始。
- 字段：`type`, `timestamp`, `task_id`, `task_name`
- 前端展示：title/status。
- 可通过 `event_to_dict` / `event_to_json` 序列化。

### `PlanCreated`

- 触发：runner 创建步骤计划。
- 字段：`type`, `timestamp`, `task_id`, `steps`
- 前端展示：plan tree。

### `StepStarted`

- 触发：进入某个 workflow step。
- 字段：`type`, `timestamp`, `task_id`, `step_index`, `step_name`
- 前端展示：active step。

### `CommandStarted`

- 触发：ShellTool 即将执行命令。
- 字段：`type`, `timestamp`, `task_id`, `command`
- 前端展示：log panel / command status。

### `CommandOutput`

- 触发：ShellTool 捕获 stdout/stderr 行。
- 字段：`type`, `timestamp`, `task_id`, `stream`, `content`
- 前端展示：log panel。

### `CommandFinished`

- 触发：命令结束。
- 字段：`type`, `timestamp`, `task_id`, `command`, `return_code`, `success`
- 前端展示：command status。

### `ErrorDetected`

- 触发：parser 识别错误或 unknown error。
- 字段：`type`, `timestamp`, `task_id`, `error_type`, `summary`, `evidence`
- 前端展示：error card。

### `FailureMemoryCreated`

- 触发：FailureMemoryBuilder 生成失败记忆。
- 字段：`type`, `timestamp`, `task_id`, `error_type`, `evidence`, `root_cause_hypothesis`, `repair_action`
- 前端展示：reflection/memory card。

### `PatchProposed`

- 触发：PatchPlanner 生成 patch plan。
- 字段：`type`, `timestamp`, `task_id`, `target_file`, `suspected_line`, `confidence`, `proposed_change`, `unified_diff`
- 前端展示：diff panel。

### `PatchApprovalRequired`

- 触发：RepairPolicy 要求显式确认，patch 未被应用。
- 字段：`type`, `timestamp`, `task_id`, `target_file`, `message`, `unified_diff`
- 前端展示：permission prompt。

### `PatchApplied`

- 触发：PatchApplier 尝试应用 patch 后。
- 字段：`type`, `timestamp`, `task_id`, `target_file`, `success`, `message`, `unified_diff`
- 前端展示：patch status。

### `VerificationStarted`

- 触发：patch 应用后，即将运行 verification command。
- 字段：`type`, `timestamp`, `task_id`, `command`, `cwd`
- 前端展示：verification status。

### `VerificationFinished`

- 触发：verification command 结束。
- 字段：`type`, `timestamp`, `task_id`, `command`, `return_code`, `success`, `summary`
- 前端展示：verification result。

### `TaskFinished`

- 触发：任务最终结束。
- 字段：`type`, `timestamp`, `task_id`, `status`, `summary`
- 前端展示：final status。

M14 没有新增 `WorkspaceCreated` / `ScoreGenerated` 事件；workspace 和 score 当前体现在 result/summary 字段中。

---

## 6. BackendController public API 当前状态

前端推荐只使用：

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
```

`BackendController` public API 必须保持：

```python
list_tasks() -> list[TaskInfo]
get_task(task_id: str) -> BenchmarkTask
run_task(task_id: str, mode: str, confirm_apply: bool = False) -> AsyncIterator[Event]
```

`mode` 当前只能是：

- `diagnosis`
- `repair`

不要改成 `diagnose`。

前端约束：

- 前端应该只依赖 `BackendController`。
- 前端不应该直接依赖内部 runner / tool / patcher。
- `run_task` 通过 async iterator 输出事件流。
- `event_serializer` 把内部 Pydantic event 转成前端稳定可消费的 dict/json-like 结构。
- M13/M14 没有破坏这个 public API。

推荐前端消费示例：

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict

controller = BackendController()

async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="repair",
    confirm_apply=True,
):
    payload = event_to_dict(event)
    print(payload)
```

---

## 7. M13 详细交接：benchmark 扩展到 6 个任务

M13 做了：

- benchmark 从 3 个任务扩展到 6 个任务。
- 新增：
  - `repair_missing_file_004`
  - `repair_entrypoint_error_005`
  - `repair_label_shape_006`
- 增强 `traceback_parser`：
  - `missing_file`
  - `entrypoint_error`
  - `label_shape`
- 增强 `failure_memory`：
  - 为新 error_type 增加 root cause 和 repair action。
- 增强 `patch_planner`：
  - `entrypoint_error`: `mainn()` -> `main()`
  - `label_shape`: `(batch_size + 1,)` -> `(batch_size,)`
  - `missing_file`: 返回 None。
- 保持 `missing_module` diagnosis-only。
- 保持 `BackendController` public API 不变。

当前 6 个任务名称：

- `repair_tensor_shape_001`
- `repair_dtype_mismatch_002`
- `repair_missing_module_003`
- `repair_missing_file_004`
- `repair_entrypoint_error_005`
- `repair_label_shape_006`

真实仓库中没有 `repair_device_mismatch_002`；当前第二个任务是 `repair_dtype_mismatch_002`。未发现需要清理的旧命名 benchmark 目录。

M13 后测试结果：

```text
65 passed
```

M14 后当前真实结果：

```text
68 passed
```

---

## 8. M14 详细交接：Hidden Evaluator / Workspace Copy / score.json

### 8.1 WorkspaceManager

新增文件：

- `scicodepilot/eval/workspace.py`

职责：

- 为每次 task run 创建 isolated workspace。
- 从 `BenchmarkTask.repo_dir` 复制原始 repo 到 workspace repo。
- 后续 original command / patch / verification / hidden evaluator 都在 workspace repo 中执行。
- 不再修改 `benchmark/tasks/*/repo` 原始目录。

核心 API：

```python
WorkspaceManager().create_workspace(task, run_id=None) -> WorkspaceInfo
```

`WorkspaceInfo` 字段：

- `task_id`
- `run_id`
- `source_repo_dir`
- `workspace_root`
- `workspace_repo_dir`

workspace 路径规则：

```text
outputs/workspaces/<run_id>/<task_id>/
```

workspace repo：

```text
outputs/workspaces/<run_id>/<task_id>/repo
```

### 8.2 ScoreResult / HiddenEvalScore

新增文件：

- `scicodepilot/eval/score_result.py`

当前模型名：

- `ScoreResult`

字段：

- `task_id: str`
- `success: bool`
- `score: float`
- `verification_command: str`
- `return_code: int | None`
- `message: str`
- `score_path: str | None`
- `checks: dict[str, bool]`

写入位置：

```text
outputs/workspaces/<run_id>/<task_id>/score.json
```

### 8.3 HiddenEvaluator

新增文件：

- `scicodepilot/eval/hidden_evaluator.py`

行为：

- `HiddenEvaluator.evaluate(task, workspace_repo_dir)`
- 在 `workspace_repo_dir` 下运行 `task.entry_command`
- `return_code == 0` 时：
  - `success=True`
  - `score=1.0`
- `return_code != 0` 时：
  - `success=False`
  - `score=0.0`
- 写入 workspace 下的 `score.json`
- 返回 `ScoreResult`

当前只是最小可用 hidden evaluator；未来可扩展成真正 hidden tests。

### 8.4 RepairBenchmarkRunner 改动

`RepairBenchmarkRunner` 现在：

- 开始时先创建 workspace。
- original command 在 `workspace_repo_dir` 下运行。
- `PatchPlanner` 读取 workspace 中的 `train.py`。
- `PatchApplier` 修改 workspace 中的目标文件。
- verification 在 `workspace_repo_dir` 下运行。
- `HiddenEvaluator` 也在 `workspace_repo_dir` 下运行。
- 原始 `benchmark/tasks/*/repo` 不应被修改。
- `PatchPlan.target_file` 是相对路径，应相对于 `workspace_repo_dir`。

### 8.5 Suite runner 改动

`BenchmarkCaseResult` 新增：

- `score: float | None`
- `score_path: str | None`
- `workspace_repo_dir: str | None`

`BenchmarkSuiteSummary` 新增：

- `total_score`
- `average_score`
- `scored_task_count`

语义：

- diagnosis mode 不一定有 score。
- repair mode `confirm_apply=False` 不应生成 score，score 为 None。
- repair mode `confirm_apply=True` 时，自动 patch 的任务应生成 `score.json`。

### 8.6 M14 测试

新增/修改测试：

- `tests/test_workspace.py`
  - 测试 workspace copy。
  - 测试修改 workspace 不影响原始 repo。
- `tests/test_hidden_evaluator.py`
  - 测试 fixed workspace `score=1.0`。
  - 测试 unfixed workspace `score=0.0`。
- `tests/test_repair_runner.py`
  - 增加 workspace/score 断言。
- `tests/test_suite_runner.py`
  - 增加 score summary 断言。

---

## 9. 当前命令清单

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

跑 frontend contract demo：

```bash
python scripts/run_frontend_contract_demo.py
```

检查原始 benchmark bug 没被污染：

```bash
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py
```

期望仍看到：

```text
classifier_expected_dim = 128
dtype=torch.float64
mainn()
batch_size + 1
```

missing_module 原始 bug 检查：

```bash
grep "definitely_missing_scicodepilot_dependency" benchmark/tasks/repair_missing_module_003/repo/train.py
```

missing_file 原始 bug 检查：

```bash
grep "data/train.csv" benchmark/tasks/repair_missing_file_004/repo/train.py
```

---

## 10. 当前测试状态

本交接文档生成前实际运行：

```bash
pytest -q
```

结果：

```text
68 passed in 23.88s
```

M14 开发阶段实际确认过：

Diagnosis suite：

```text
mode: diagnosis
total_tasks: 6
diagnosis_pass_count: 6
patch_plan_count: 4
patch_applied_count: 0
verification_success_count: 0
scored_task_count: 0
total_score: 0.0
average_score: 0.0
```

Repair suite 默认无确认：

```text
mode: repair
total_tasks: 6
diagnosis_pass_count: 0
patch_plan_count: 4
patch_applied_count: 0
verification_success_count: 0
scored_task_count: 0
total_score: 0.0
average_score: 0.0
```

Repair suite `--confirm-apply`：

```text
mode: repair
total_tasks: 6
diagnosis_pass_count: 0
patch_plan_count: 4
patch_applied_count: 4
verification_success_count: 4
scored_task_count: 4
total_score: 4.0
average_score: 1.0
```

本交接文档生成前确认：

- `score.json` 已存在于 `outputs/workspaces/.../score.json`。
- `outputs/workspaces` 路径正常。
- 原始 benchmark repo 未被污染。
- `BackendController` public API 未改变。

本次文档生成时没有重新运行三种 suite，只复用了 M14 阶段已实际运行并记录的结果。建议下一个 Codex 开工前可按第 9 节命令重新确认。

---

## 11. 当前已知坑和设计约束

- 所有命令必须在 WSL Ubuntu 中运行，不要在 Windows PowerShell 中运行。
- Python 命令必须在 `scicodepilot-dev` conda 环境下运行。
- 早期曾在 PowerShell 环境遇到 `pydantic` import 问题，不代表 WSL conda 环境有问题。
- 运行某些 WSL 命令时输出里可能夹杂 WSL localhost/NAT 乱码 warning，通常不影响 Python 结果。
- `diagnosis` 是合法 mode；不要改成 `diagnose`。
- diagnosis mode 不应该修改代码。
- repair mode `confirm_apply=False` 不应该 apply patch。
- repair mode `confirm_apply=True` 才能 apply patch。
- M14 后即使 apply patch，也只能修改 workspace repo，不能修改 benchmark 原始 repo。
- `PatchApplier` 是最小文本替换器，不是通用 patch engine。
- `HiddenEvaluator` 当前只是最小版本，不是真正复杂 hidden tests。
- `score.json` 目前只是基于 `entry_command` return code 的基础评分。
- `BackendController` public API 不要随便改。
- 前端只依赖 `BackendController` 和 `event_serializer`。
- `missing_module` / `missing_file` 当前仍然 diagnosis-only，下一步 M15 要做 EnvDoctor。
- parser 规则表是逐行扫描 stderr，匹配到的第一条规则会返回。若未来出现 warning 抢先误判，需要调整规则顺序或过滤 warning。
- 特别注意：曾讨论过 numpy 缺失 warning 可能导致 parser 误判 `missing_module`。当前真实任务中未复现，但未来扩展 PyTorch/NumPy 任务时要留意。

---

## 12. 下一阶段 M15 建议

建议下一阶段：

```text
M15：EnvDoctor，专门处理 missing_module / missing_file。
```

建议目标：

- 新增 `scicodepilot/doctor/env_doctor.py`。
- 定义：
  - `EnvDiagnosis`
  - `EnvRepairAdvice`
- 对 `missing_module`：
  - 从 stderr evidence 中提取模块名。
  - 生成建议命令，例如：

```bash
python -m pip install <module>
```

- 对 `missing_file`：
  - 从 stderr evidence 中提取缺失文件路径。
  - 生成检查路径、恢复文件、确认工作目录等建议。
- 不要自动 `pip install`。
- 不要自动创建缺失文件。
- 可新增事件：
  - `EnvDiagnosisCreated`
- suite summary 可新增：
  - `env_diagnosis_count`
  - `missing_module_count`
  - `missing_file_count`
- 保持 `BackendController` public API 不变。
- 保持 M14 workspace / score.json 能力不被破坏。

---

## 13. 给下一个 Codex 的继续开发 Prompt

下面是一段可直接复制给下一个 Codex 对话的 prompt：

```text
你正在继续开发 SciCodePilot 项目后端。

项目路径：
/home/zengl/projects/SciCodePilot

运行环境：
WSL Ubuntu
Conda 环境：scicodepilot-dev

非常重要：
所有命令必须在 WSL Ubuntu 中运行，不要在 Windows PowerShell 中运行。
涉及 Python / pip 时，优先使用当前 conda 环境中的 python / pip。

进入项目后先执行：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev

当前项目已完成 M1–M14：
- benchmark 已扩展到 6 个任务：
  - repair_tensor_shape_001
  - repair_dtype_mismatch_002
  - repair_missing_module_003
  - repair_missing_file_004
  - repair_entrypoint_error_005
  - repair_label_shape_006
- BackendController 是前端稳定 public API：
  - list_tasks()
  - get_task(task_id)
  - run_task(task_id, mode, confirm_apply=False)
- mode 只能是 "diagnosis" 或 "repair"，不要改成 "diagnose"。
- M14 已实现 isolated workspace：
  - outputs/workspaces/<run_id>/<task_id>/repo
- repair apply / verification / hidden evaluator 都在 workspace repo 中执行，不污染 benchmark/tasks/*/repo。
- HiddenEvaluator 当前会基于 entry_command return_code 写 score.json。
- 当前 pytest -q 应为 68 passed。

本阶段目标：M15 EnvDoctor，专门处理 missing_module / missing_file。

请不要接入 LLM、OpenHands、LangGraph、Textual UI。
请不要自动 pip install。
请不要自动创建缺失文件。
请保持 BackendController public API 不变。

建议新增文件：
- scicodepilot/doctor/__init__.py
- scicodepilot/doctor/env_doctor.py
- tests/test_env_doctor.py

建议实现：
- EnvDiagnosis(BaseModel)
  - error_type
  - extracted_target
  - evidence
  - summary
- EnvRepairAdvice(BaseModel)
  - error_type
  - target
  - recommendation
  - suggested_commands
  - safe_to_auto_apply: bool = False
- EnvDoctor
  - diagnose(parsed_error: ParsedError) -> EnvDiagnosis | None
  - advise(env_diagnosis: EnvDiagnosis) -> EnvRepairAdvice

行为要求：
- 对 missing_module，从 evidence 提取模块名，例如 definitely_missing_scicodepilot_dependency。
- 生成建议命令：python -m pip install <module>
- 但不要执行该命令。
- 对 missing_file，从 evidence 提取缺失路径，例如 data/train.csv。
- 生成检查路径/恢复文件/确认工作目录的建议。
- 不要创建文件。

可选事件：
- 在 scicodepilot/events/schema.py 新增 EnvDiagnosisCreated。
- 如果新增事件，请补 event_serializer 测试和前端 contract 文档。

接入建议：
- RepairBenchmarkRunner 在 parsed_error 为 missing_module / missing_file 且 patch_plan 为 None 时，可以调用 EnvDoctor 生成 advice。
- suite result 可增加 env_diagnosis/advice 相关字段。
- frontend_contract.md 更新 UI 建议映射。

测试要求：
- pytest -q 全部通过。
- 新增测试覆盖 missing_module 提取模块名。
- 新增测试覆盖 missing_file 提取文件路径。
- 确认 EnvDoctor 不执行 pip install、不创建文件。
- 确认 BackendController.run_task(...) 仍正常 yield Event。
- 确认 benchmark 原始 bug 未被污染：
  grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
  grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
  grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
  grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py

验证命令：
pytest -q
python scripts/run_benchmark_suite.py --mode diagnosis
python scripts/run_benchmark_suite.py --mode repair
python scripts/run_benchmark_suite.py --mode repair --confirm-apply

完成后请总结：
- 新增/修改文件
- EnvDoctor 支持的 error_type
- 是否新增事件
- pytest 结果
- suite 结果
- 是否保持 BackendController public API 不变
- 是否确认原始 benchmark repo 未被污染
```

