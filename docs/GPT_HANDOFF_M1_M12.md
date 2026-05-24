SciCodePilot 0–M12 技术交接文档

用途：本文件用于在新 ChatGPT/Codex 窗口中继续开发 SciCodePilot 后端。
范围：补充高层项目方案 md 文件没有覆盖的实际开发上下文，记录从 M0 环境搭建到 M12 后端接口交付的真实实现过程。
当前状态：后端 MVP 主链路已经完成，可以交给前端同学通过 BackendController 联调；后续可继续做 M13 前后端联调、防坑补丁、扩展 benchmark、hidden evaluator、EnvDoctor、LLM Planner/Fixer/Reviewer。

0. 项目基本信息
项目名称
SciCodePilot
本地项目路径
/home/zengl/projects/SciCodePilot
Conda 环境
scicodepilot-dev
运行环境约定

| 层级          | 选择                                                |
| ----------- | ------------------------------------------------- |
| 操作系统        | **Windows + WSL2 Ubuntu 22.04 LTS**               |
| Python 环境管理 | **Conda / Miniconda**                             |
| 后端开发 Python | **Python 3.10**                                   |
| GPU 任务执行    | **保留你已经跑通的 PyTorch nightly CUDA 12.8 环境**         |
| 编辑器         | **VSCode Remote - WSL** |
| 版本管理        | Git                                               |
| 后端核心        | `asyncio`、`pydantic`、`rich`、`pytest`              |

采用之前已经验证过能跑我的 RTX 5060 Ti 的环境配置方案：
Python 3.10
PyTorch 2.12.0.dev20260228+cu128
conda install -c nvidia cuda-toolkit=12.8 -y
环境 A：后端开发环境 scicodepilot-dev
环境 B：GPU 任务运行环境 scicodepilot-gpu

后续所有命令都必须在 WSL Ubuntu 中执行。
不要在 Windows PowerShell 中运行项目命令，尤其不要从 Windows PowerShell 里直接运行：

python scripts/xxx.py

正确方式是进入 WSL Ubuntu 终端后运行：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev

如果涉及 Python / pip，优先使用当前 conda 环境中的：

python
python -m pip

不要随意使用系统 Python，也不要在 Windows 环境里安装依赖。

1. 当前项目总体定位

SciCodePilot 是一个面向科研代码复现、实验环境诊断与代码自修复的终端 Agent 后端。

本窗口实际开发重点不是完整 LLM Agent，而是先打通一个稳定的后端闭环：

benchmark task
→ 执行命令
→ 捕获 stdout/stderr
→ 解析错误
→ 生成结构化 failure memory
→ 生成 PatchPlan
→ 权限确认
→ 可选 apply patch
→ verification
→ 恢复 benchmark 原始 bug
→ 生成事件流
→ 给前端提供 BackendController

当前系统已经做到：

M0 环境与目录
M1 EventBus
M2 ShellTool
M3 TracebackParser + FailureMemory
M4 多类错误规则 + 单元测试
M5 第一个 benchmark diagnosis task
M6 真实 PyTorch shape bug task
M7 PatchPlan
M8 PatchApplier + RepairResult
M9 repair workflow 事件化
M10 confirmation policy
M11 多任务 benchmark suite + JSONL/summary
M12 BackendController + frontend contract
2. M0–M12 里程碑交接
M0：环境与项目骨架
目标

建立 SciCodePilot 后端开发环境，明确使用：

WSL Ubuntu + Conda + Python 3.10
关键结论

推荐路线是：

WSL2 Ubuntu + Conda 环境

而不是 Windows 原生 PowerShell / Anaconda 命令行。

原因：

后端需要运行 shell 命令；
后端需要模拟科研仓库执行；
后续可能接 Docker / Textual；
Linux 路径、权限、子进程语义更适合该项目。
环境信息
项目路径: /home/zengl/projects/SciCodePilot
Conda 环境: scicodepilot-dev
Python: 3.10
建议基础依赖

早期安装过：

pip install pydantic rich pyyaml python-dotenv pytest pytest-asyncio ruff

后续因为真实 PyTorch benchmark 需要，又安装了：

python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install numpy

注意：M6 的 PyTorch task 是 CPU-only，不要求 CUDA，不需要使用 RTX 5060 Ti。

验证命令
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
python --version
which python
which pip
M1：异步事件队列 EventBus
目标

先不接 LLM，不接 Textual，不真实执行 shell。
只打通最小的同进程异步事件流：

Orchestrator
→ EventBus(asyncio.Queue)
→ consumer
→ 终端打印事件
新增/修改文件
scicodepilot/events/schema.py
scicodepilot/events/bus.py
scicodepilot/agent/demo_orchestrator.py
scripts/run_backend_demo.py
关键实现
schema.py

定义 Pydantic 事件模型。

早期事件包括：

TaskStarted
PlanCreated
StepStarted
CommandStarted
CommandOutput
ErrorDetected
FailureMemoryCreated
TaskFinished

并定义联合类型：

Event = (
    TaskStarted
    | PlanCreated
    | StepStarted
    | CommandStarted
    | CommandOutput
    | ErrorDetected
    | FailureMemoryCreated
    | TaskFinished
)
bus.py

实现最小事件总线：

class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def emit(self, event: Event) -> None:
        await self.queue.put(event)

    async def next_event(self) -> Event:
        return await self.queue.get()

后续还提供了 queue_size，方便测试中读取当前队列事件。

demo_orchestrator.py

早期是假 Agent，按固定顺序发事件：

TaskStarted
PlanCreated
StepStarted
CommandStarted
CommandOutput
ErrorDetected
FailureMemoryCreated
TaskFinished
run_backend_demo.py

创建：

EventBus
DemoOrchestrator
consumer

并发运行：

orchestrator.run()
consumer(event_bus)

consumer 收到 TaskFinished 后退出。

验证结果

运行：

python scripts/run_backend_demo.py

可看到事件顺序正确，consumer 正常退出。

M2：真实 ShellTool
目标

把 M1 中人工伪造的命令输出，升级为真实执行 shell 命令：

ShellTool
→ asyncio.create_subprocess_shell
→ stdout/stderr 实时读取
→ CommandOutput 事件
→ CommandFinished 事件
新增/修改文件

新增：

scicodepilot/tools/shell_tool.py
scripts/mock_training_error.py

修改：

scicodepilot/events/schema.py
scicodepilot/agent/demo_orchestrator.py
scripts/run_backend_demo.py
关键事件新增
CommandFinished

字段包括：

type: Literal["CommandFinished"]
task_id: str
command: str
return_code: int
success: bool
ShellTool 核心逻辑
class ShellTool:
    async def run(self, task_id: str, command: str) -> int:
        ...

后来在 M3 改为返回 CommandResult。

M2 阶段核心行为：

emit CommandStarted
使用 asyncio.create_subprocess_shell(...)
并发读取 stdout / stderr
每行输出 emit CommandOutput
子进程结束后 emit CommandFinished
返回 return code
mock_training_error.py

用于模拟失败脚本：

stdout:
Loading dataset...
Building model...

stderr:
RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)

exit code:
1
验证结果
python scripts/run_backend_demo.py

关键输出：

[CommandStarted] python scripts/mock_training_error.py
[stdout] Loading dataset...
[stdout] Building model...
[stderr] RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)
[CommandFinished] return_code=1 success=False
M3：CommandResult + TracebackParser + FailureMemory
目标

让诊断不再由 DemoOrchestrator 手写固定内容，而是从真实 stderr 自动生成：

CommandResult
→ TracebackParser
→ ParsedError
→ FailureMemoryBuilder
→ FailureMemoryCreated
新增文件
scicodepilot/tools/command_result.py
scicodepilot/tools/traceback_parser.py
scicodepilot/memory/failure_memory.py
修改文件
scicodepilot/tools/shell_tool.py
scicodepilot/agent/demo_orchestrator.py
关键类
CommandResult

路径：

scicodepilot/tools/command_result.py

字段：

class CommandResult(BaseModel):
    command: str
    return_code: int
    success: bool
    stdout_lines: list[str]
    stderr_lines: list[str]

区别：

CommandOutput = 流式事件
CommandResult = 命令结束后的完整汇总
ParsedError

路径：

scicodepilot/tools/traceback_parser.py

字段：

class ParsedError(BaseModel):
    error_type: str
    summary: str
    evidence: list[str]
TracebackParser

M3 第一版只识别：

mat1 and mat2 shapes cannot be multiplied

生成：

error_type = tensor_shape
FailureMemory

路径：

scicodepilot/memory/failure_memory.py

字段：

class FailureMemory(BaseModel):
    error_type: str
    evidence: list[str]
    root_cause_hypothesis: str
    repair_action: str
FailureMemoryBuilder

根据 ParsedError 生成结构化 failure memory。

验证结果
python scripts/run_backend_demo.py

输出中：

[ErrorDetected] tensor_shape
[FailureMemoryCreated] tensor_shape

并且不是 orchestrator 手写，而是 parser + memory builder 生成。

M4：TracebackParser 规则表 + 单元测试
目标

把 parser 从单条 if 升级成可扩展规则表，并补测试。

修改文件
scicodepilot/tools/traceback_parser.py
scicodepilot/memory/failure_memory.py
tests/test_shell_tool.py
新增测试文件
tests/test_traceback_parser.py
tests/test_failure_memory.py
关键结构
@dataclass(frozen=True)
class ErrorRule:
    error_type: str
    patterns: tuple[str, ...]
    summary: str

ERROR_RULES = (...)
当前支持错误类型
tensor_shape
device_mismatch
dtype_mismatch
missing_module
规则示例
tensor_shape

匹配：

mat1 and mat2 shapes cannot be multiplied
size mismatch
device_mismatch

匹配：

Expected all tensors to be on the same device
found at least two devices
dtype_mismatch

匹配：

expected scalar type
mat1 and mat2 must have the same dtype
Found dtype
have the same dtype

后续 M11 增加了 have the same dtype。

missing_module

匹配：

ModuleNotFoundError
No module named
验证结果

当时：

pytest -q

结果：

11 passed

后续测试数量继续增加。

M5：第一个正式 benchmark diagnosis task
目标

把早期 mock demo 升级成正式 benchmark 任务夹具：

benchmark/tasks/repair_tensor_shape_001

并实现 diagnosis-only benchmark 闭环：

load metadata
→ run entry command in repo/
→ parse stderr
→ build failure memory
→ compare expected_diagnosis.json
→ diagnosis_passed
新增 benchmark 文件
benchmark/tasks/repair_tensor_shape_001/task.md
benchmark/tasks/repair_tensor_shape_001/metadata.json
benchmark/tasks/repair_tensor_shape_001/repo/train.py
benchmark/tasks/repair_tensor_shape_001/reference/expected_diagnosis.json
新增后端模块
scicodepilot/eval/task_loader.py
scicodepilot/eval/diagnosis_evaluator.py
scicodepilot/eval/diagnosis_runner.py
新增脚本
scripts/run_benchmark_diagnosis_demo.py
新增测试
tests/test_task_loader.py
tests/test_diagnosis_evaluator.py
关键类/函数
BenchmarkTask

路径：

scicodepilot/eval/task_loader.py

字段包括：

task_id: str
task_name: str
category: str
difficulty: str
entry_command: str
task_dir: str
repo_dir: str
expected_diagnosis_path: str
requires: list[str]

requires 是 M6 后加入的。

load_benchmark_task(...)

读取 metadata.json 并返回 BenchmarkTask。

ExpectedDiagnosis

路径：

scicodepilot/eval/diagnosis_evaluator.py

字段：

expected_error_type: str
expected_summary_keywords: list[str]
expected_root_cause_keywords: list[str]
expected_repair_action_keywords: list[str]
evaluate_diagnosis(...)

检查：

error_type
summary keywords
root cause keywords
repair action keywords

四项全 True 才算通过。

DiagnosisBenchmarkRunner

路径：

scicodepilot/eval/diagnosis_runner.py

完成：

TaskStarted
PlanCreated
StepStarted
ShellTool.run
TracebackParser.parse
FailureMemoryBuilder
evaluate_diagnosis
TaskFinished
验证结果
python scripts/run_benchmark_diagnosis_demo.py

期望：

diagnosis_passed: True
M6：真实轻量 PyTorch shape bug
目标

把 repair_tensor_shape_001 从标准库模拟 stderr 升级成真实 PyTorch shape mismatch。

修改文件
benchmark/tasks/repair_tensor_shape_001/task.md
benchmark/tasks/repair_tensor_shape_001/metadata.json
benchmark/tasks/repair_tensor_shape_001/repo/train.py
scicodepilot/eval/task_loader.py
tests/test_task_loader.py

新增测试：

tests/test_repair_tensor_shape_task.py
关键变更
train.py

改为真实 PyTorch 代码：

import torch
from torch import nn

device = torch.device("cpu")

batch_size = 32
upstream_feature_dim = 64
classifier_expected_dim = 128
num_classes = 10

x = torch.randn(batch_size, upstream_feature_dim, device=device)
classifier = nn.Linear(classifier_expected_dim, num_classes).to(device)
logits = classifier(x)

真实触发：

RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)

不手写 stderr。

CPU-only

明确不使用 CUDA：

device = torch.device("cpu")
metadata.json

加入：

"requires": ["torch"]
踩坑

当前环境最开始没有 torch：

ModuleNotFoundError: No module named 'torch'

按要求当时没有乱装，后续建议安装 CPU 版：

python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
验证结果

安装 torch 后：

pytest -q
python scripts/run_benchmark_diagnosis_demo.py

应看到真实 PyTorch traceback，并最终：

diagnosis_passed: True
M7：PatchPlan / 自动修复前的 diff 草案
目标

不真正修改文件，只根据诊断结果和源码生成结构化 patch plan。

ParsedError
+ FailureMemory
+ repo/train.py
→ PatchPlan
新增 repair 模块
scicodepilot/repair/__init__.py
scicodepilot/repair/patch_plan.py
scicodepilot/repair/patch_planner.py
修改文件
scicodepilot/eval/diagnosis_runner.py
scripts/run_benchmark_diagnosis_demo.py
新增测试
tests/test_patch_planner.py
PatchPlan

字段：

class PatchPlan(BaseModel):
    task_id: str
    error_type: str
    target_file: str
    suspected_line: int | None
    rationale: str
    proposed_change: str
    unified_diff: str
    confidence: float
PatchPlanner

当前支持：

tensor_shape
dtype_mismatch
tensor_shape 规则

定位：

classifier_expected_dim = 128

建议改为：

classifier_expected_dim = 64

生成 unified diff：

-    classifier_expected_dim = 128
+    classifier_expected_dim = 64
dtype_mismatch 规则

M11 时增加。

定位：

dtype=torch.float64

建议改为：

dtype=torch.float32
missing_module

不生成 patch plan，因为缺依赖属于环境问题，适合后续 EnvDoctor，而不是改源码。

验证结果

当时：

pytest -q

结果：

19 passed

run_benchmark_diagnosis_demo.py 最终会展示 Patch Plan，但不改文件。

M8：PatchApplier + RepairResult
目标

支持手动应用 M7 生成的 patch，并重新运行验证命令，但必须在结束后恢复原始 benchmark bug。

新增文件
scicodepilot/repair/repair_result.py
scicodepilot/repair/patch_applier.py
scripts/run_benchmark_repair_demo.py
tests/test_patch_applier.py
修改文件
scicodepilot/repair/__init__.py
RepairResult

字段：

class RepairResult(BaseModel):
    task_id: str
    patch_applied: bool
    target_file: str | None
    verification_command: str
    verification_success: bool
    verification_return_code: int | None
    message: str

M10 后又新增：

patch_plan_generated: bool = False
requires_confirmation: bool = False
confirmation_granted: bool = False
PatchApplier

只支持简单单文件 unified diff 文本替换。

支持这种 diff：

-    classifier_expected_dim = 128
+    classifier_expected_dim = 64

重要约束：

不调用 shell patch
不调用 git apply
不搜索任意文件
只修改 patch_plan.target_file
找不到 old line 就返回 False
失败时不应修改文件
run_benchmark_repair_demo.py

早期流程：

diagnosis
→ patch plan
→ apply
→ verification
→ restore original file

M10 后增加 confirmation 参数。

验证结果
pytest -q
23 passed

确认 repair demo 后：

classifier_expected_dim = 128

仍保留原始 bug。

M9：repair workflow 接入事件流
目标

让修复过程也通过 EventBus 可观察，而不是只在脚本 summary 中出现。

新增事件
PatchApplied
VerificationStarted
VerificationFinished
修改文件
scicodepilot/events/schema.py
scripts/run_benchmark_repair_demo.py
scicodepilot/repair/__init__.py
新增文件
scicodepilot/repair/repair_runner.py
tests/test_repair_events.py
tests/test_repair_runner.py
RepairBenchmarkRunner

路径：

scicodepilot/repair/repair_runner.py

完整流程：

TaskStarted
PlanCreated
StepStarted: Run original benchmark command
ShellTool.run
ErrorDetected
FailureMemoryCreated
PatchPlan
PatchApplied
VerificationStarted
ShellTool.run verification
VerificationFinished
restore original file
TaskFinished

重要约束：

不调用 DiagnosisBenchmarkRunner
避免诊断阶段提前 TaskFinished
整个 repair workflow 只发一次最终 TaskFinished
使用 try/finally 恢复原始 benchmark 文件
验证结果

当时：

pytest -q
27 passed

关键事件：

[PatchApplied] success=True target_file=train.py
[VerificationStarted] python train.py
[VerificationFinished] success=True return_code=0
[TaskFinished] success - Repair workflow completed successfully; original benchmark file was restored.
M10：RepairPolicy / confirmation gate
目标

给 repair workflow 增加权限控制：

默认：只提案，不 apply
显式确认：apply + verification
新增事件
PatchProposed
PatchApprovalRequired
新增文件
scicodepilot/repair/repair_policy.py
tests/test_repair_policy.py
修改文件
scicodepilot/events/schema.py
scicodepilot/repair/repair_result.py
scicodepilot/repair/repair_runner.py
scicodepilot/repair/__init__.py
scripts/run_benchmark_repair_demo.py
tests/test_repair_events.py
tests/test_repair_runner.py
RepairPolicy
class RepairPolicy(BaseModel):
    require_confirmation: bool = True
    approved: bool = False

    def can_apply_patch(self) -> bool:
        return (not self.require_confirmation) or self.approved

语义：

require_confirmation=True, approved=False
→ 只生成 PatchPlan，不 apply

require_confirmation=True, approved=True
→ 显式确认后 apply

require_confirmation=False
→ 自动模式，允许 apply
CLI 参数

run_benchmark_repair_demo.py 新增：

--confirm-apply

默认：

python scripts/run_benchmark_repair_demo.py

只生成 patch plan：

[PatchProposed]
[PatchApprovalRequired]
patch_applied: False
verification_success: False

显式确认：

python scripts/run_benchmark_repair_demo.py --confirm-apply

执行 apply + verification：

[PatchApplied]
[VerificationStarted]
[VerificationFinished] success=True
验证结果
pytest -q
34 passed
M11：多任务 benchmark suite + JSONL/summary
目标

从单任务扩展到多任务 benchmark suite，并输出长期评测产物：

results.jsonl
summary.json
新增 benchmark tasks
1. repair_dtype_mismatch_002

路径：

benchmark/tasks/repair_dtype_mismatch_002

用途：

真实 PyTorch CPU dtype mismatch。

文档说明：该任务包含一个最小 PyTorch 脚本，因为矩阵乘法接收不兼容 dtype 的 tensors 而失败；它 diagnosis-first，并且可以通过对齐 tensor dtype 来修复；运行在 CPU，不需要 CUDA。

关键逻辑：

x = torch.randn(4, 4, dtype=torch.float32)
w = torch.randn(4, 4, dtype=torch.float64)
y = x @ w

触发 dtype mismatch。

支持：

diagnosis
repair confirm-apply

PatchPlanner 会生成：

-    w = torch.randn(4, 4, dtype=torch.float64)
+    w = torch.randn(4, 4, dtype=torch.float32)
2. repair_missing_module_003

路径：

benchmark/tasks/repair_missing_module_003

用途：

Python 缺模块错误。

文档说明：该任务包含一个最小 Python 脚本，因为可选科学依赖无法导入而失败；当前是 diagnosis-only，缺依赖更适合环境修复工具处理，而不是修改 benchmark 脚本。

关键逻辑：

print("Importing optional scientific dependency...", flush=True)
import definitely_missing_scicodepilot_dependency

支持：

diagnosis

不生成 patch plan。

新增 suite runner 模块
scicodepilot/eval/suite_result.py
scicodepilot/eval/suite_runner.py
scripts/run_benchmark_suite.py
新增测试
tests/test_benchmark_tasks.py
tests/test_suite_runner.py
BenchmarkCaseResult

字段包括：

task_id: str
mode: str
command_success: bool | None
parsed_error_type: str | None
diagnosis_passed: bool | None
patch_plan_generated: bool | None
patch_applied: bool | None
verification_success: bool | None
verification_return_code: int | None
message: str
BenchmarkSuiteSummary

字段包括：

total_tasks: int
mode: str
diagnosis_pass_count: int
patch_plan_count: int
patch_applied_count: int
verification_success_count: int
run_benchmark_suite.py

支持：

--mode diagnosis
--mode repair
--confirm-apply
--tasks <task_id...>
--output-dir outputs/benchmark_runs

输出：

outputs/benchmark_runs/<timestamp>/results.jsonl
outputs/benchmark_runs/<timestamp>/summary.json
验证结果
pytest -q
40 passed
Diagnosis suite
mode: diagnosis
total_tasks: 3
diagnosis_pass_count: 3
patch_plan_count: 2
patch_applied_count: 0
verification_success_count: 0
Repair 默认无确认
mode: repair
total_tasks: 3
diagnosis_pass_count: 0
patch_plan_count: 2
patch_applied_count: 0
verification_success_count: 0
Repair 显式确认
mode: repair
total_tasks: 3
diagnosis_pass_count: 0
patch_plan_count: 2
patch_applied_count: 2
verification_success_count: 2
M12：BackendController + 前端 contract
目标

给前端同学提供稳定、干净、可调用的后端接口层。
前端不需要理解内部 runner/tool，只调用：

BackendController
event_to_dict
event_to_json

frontend_contract.md 已说明这是 Textual 前端推荐使用的稳定后端入口，前端应把 BackendController 当作 public API。

新增 backend 接口文件
scicodepilot/backend/__init__.py
scicodepilot/backend/controller.py
scicodepilot/backend/event_serializer.py
scicodepilot/backend/frontend_contract.md
新增 demo 和测试
scripts/run_frontend_contract_demo.py
tests/test_backend_controller.py
tests/test_event_serializer.py
BackendController

路径：

scicodepilot/backend/controller.py

暴露接口：

list_tasks() -> list[TaskInfo]

get_task(task_id: str) -> BenchmarkTask

run_task(
    task_id: str,
    mode: str,
    confirm_apply: bool = False,
) -> AsyncIterator[Event]
TaskInfo

字段：

task_id: str
task_name: str
category: str
difficulty: str
requires: list[str]

这与 contract 中说明一致。

前端推荐消费方式

正确写法：

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict

controller = BackendController()

async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="diagnosis",
    confirm_apply=False,
):
    event_dict = event_to_dict(event)

注意：用户请求中示例写的是 mode="diagnose"，但当前实际接口使用的是：

mode="diagnosis"

这一点必须在新窗口和前端联调时注意。

运行 diagnosis
async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="diagnosis",
):
    event_dict = event_to_dict(event)

contract 中也是 mode="diagnosis"。

运行 repair 默认无确认
async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="repair",
    confirm_apply=False,
):
    event_dict = event_to_dict(event)

语义：

生成 PatchPlan
发 PatchProposed
发 PatchApprovalRequired
不 apply patch
不 verification

contract 中明确说明这是默认安全 repair 模式，只提出 patch 并在应用前停止。

运行 repair 显式确认
async for event in controller.run_task(
    task_id="repair_tensor_shape_001",
    mode="repair",
    confirm_apply=True,
):
    event_dict = event_to_dict(event)

contract 中说明，只有用户明确批准后才应使用该路径。

event_serializer.py

作用：

把内部 Pydantic event 转成前端稳定可消费的 dict / JSON 字符串。

接口：

event_to_dict(event: Event) -> dict
event_to_json(event: Event) -> str

要求：

包含 type
包含 timestamp
timestamp 转成 ISO 字符串
兼容 Pydantic v1/v2
frontend_contract.md 内容

路径：

scicodepilot/backend/frontend_contract.md

内容包括：

import 方式；
list tasks；
run diagnosis；
run repair without confirmation；
run repair with explicit confirmation；
Event 到 UI 的映射；
前端推荐边界；
transport note：当前是同进程 asyncio event stream，不是 WebSocket。

contract 明确要求前端只调用：

BackendController
event_to_dict
event_to_json

不要直接调用：

ShellTool
PatchApplier
PatchPlanner
RepairBenchmarkRunner
DiagnosisBenchmarkRunner

验证结果
pytest -q
51 passed
frontend contract demo

默认运行：

python scripts/run_frontend_contract_demo.py

关键输出：

[PatchProposed] target_file=train.py confidence=0.85
[PatchApprovalRequired] target_file=train.py - Patch application requires explicit confirmation.
[TaskFinished] demo_finished - Patch plan was generated, but patch application requires explicit confirmation.

missing module diagnosis：

python scripts/run_frontend_contract_demo.py --task-id repair_missing_module_003 --mode diagnosis

关键输出：

[ErrorDetected] missing_module - The program failed because a required Python module is not installed or not importable.
[FailureMemoryCreated] missing_module
[TaskFinished] demo_finished - Benchmark diagnosis completed and matched the expected diagnosis criteria.

confirm apply：

python scripts/run_frontend_contract_demo.py --task-id repair_tensor_shape_001 --mode repair --confirm-apply

关键输出：

[PatchApplied] success=True target_file=train.py
[VerificationFinished] success=True return_code=0
[TaskFinished] success - Repair workflow completed successfully; original benchmark file was restored.
3. 当前后端代码结构

以下为当前核心结构。可能还有 __pycache__、输出目录等未列出。

SciCodePilot/
├── benchmark/
│   └── tasks/
│       ├── repair_tensor_shape_001/
│       │   ├── task.md
│       │   ├── metadata.json
│       │   ├── repo/
│       │   │   └── train.py
│       │   └── reference/
│       │       └── expected_diagnosis.json
│       │
│       ├── repair_dtype_mismatch_002/
│       │   ├── task.md
│       │   ├── metadata.json
│       │   ├── repo/
│       │   │   └── train.py
│       │   └── reference/
│       │       └── expected_diagnosis.json
│       │
│       └── repair_missing_module_003/
│           ├── task.md
│           ├── metadata.json
│           ├── repo/
│           │   └── train.py
│           └── reference/
│               └── expected_diagnosis.json
│
├── outputs/
│   └── benchmark_runs/
│       └── <timestamp>/
│           ├── results.jsonl
│           └── summary.json
│
├── scripts/
│   ├── mock_training_error.py
│   ├── run_backend_demo.py
│   ├── run_benchmark_diagnosis_demo.py
│   ├── run_benchmark_repair_demo.py
│   ├── run_benchmark_suite.py
│   └── run_frontend_contract_demo.py
│
├── scicodepilot/
│   ├── __init__.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   └── demo_orchestrator.py
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── event_serializer.py
│   │   └── frontend_contract.md
│   │
│   ├── eval/
│   │   ├── task_loader.py
│   │   ├── diagnosis_evaluator.py
│   │   ├── diagnosis_runner.py
│   │   ├── suite_result.py
│   │   └── suite_runner.py
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── bus.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   └── failure_memory.py
│   │
│   ├── repair/
│   │   ├── __init__.py
│   │   ├── patch_plan.py
│   │   ├── patch_planner.py
│   │   ├── patch_applier.py
│   │   ├── repair_policy.py
│   │   ├── repair_result.py
│   │   └── repair_runner.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── command_result.py
│       ├── shell_tool.py
│       └── traceback_parser.py
│
└── tests/
    ├── test_backend_controller.py
    ├── test_benchmark_tasks.py
    ├── test_diagnosis_evaluator.py
    ├── test_event_serializer.py
    ├── test_failure_memory.py
    ├── test_patch_applier.py
    ├── test_patch_planner.py
    ├── test_repair_events.py
    ├── test_repair_policy.py
    ├── test_repair_runner.py
    ├── test_repair_tensor_shape_task.py
    ├── test_shell_tool.py
    ├── test_suite_runner.py
    ├── test_task_loader.py
    └── test_traceback_parser.py
4. 核心文件作用说明
benchmark/tasks/*

存放 benchmark 任务。

每个任务标准结构：

task.md
metadata.json
repo/train.py
reference/expected_diagnosis.json

当前已有 3 个任务：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_missing_module_003
scicodepilot/events/schema.py

定义所有事件模型。

当前事件类型包括：

TaskStarted
PlanCreated
StepStarted
CommandStarted
CommandOutput
CommandFinished
ErrorDetected
FailureMemoryCreated
PatchProposed
PatchApprovalRequired
PatchApplied
VerificationStarted
VerificationFinished
TaskFinished

并维护 Event 联合类型。

scicodepilot/events/bus.py

定义 EventBus。

核心：

asyncio.Queue[Event]
emit()
next_event()
queue_size
scicodepilot/tools/shell_tool.py

异步执行 shell 命令。

功能：

emit CommandStarted
stream stdout/stderr as CommandOutput
emit CommandFinished
return CommandResult

支持：

run(task_id, command, cwd=None)

cwd 用于让 benchmark 命令在自己的 repo/ 目录下运行。

scicodepilot/tools/command_result.py

定义 CommandResult。

用于保存命令执行完成后的完整结果：

command
return_code
success
stdout_lines
stderr_lines
scicodepilot/tools/traceback_parser.py

规则表 parser。

输入：

stderr_lines

输出：

ParsedError | None

支持：

tensor_shape
device_mismatch
dtype_mismatch
missing_module
scicodepilot/memory/failure_memory.py

定义：

FailureMemory
FailureMemoryBuilder

根据 ParsedError 生成结构化 failure memory：

error_type
evidence
root_cause_hypothesis
repair_action
scicodepilot/eval/task_loader.py

加载 benchmark task。

核心：

load_benchmark_task(task_dir)
BenchmarkTask
scicodepilot/eval/diagnosis_evaluator.py

加载 expected diagnosis，并评估：

error_type
summary keywords
root cause keywords
repair action keywords
scicodepilot/eval/diagnosis_runner.py

单任务 diagnosis runner。

流程：

run command
parse error
build failure memory
evaluate expected diagnosis
return DiagnosisRunResult
scicodepilot/repair/patch_plan.py

定义 PatchPlan。

scicodepilot/repair/patch_planner.py

规则式 patch plan 生成器。

当前支持：

tensor_shape
dtype_mismatch

不支持：

missing_module
scicodepilot/repair/patch_applier.py

最小安全 patch applier。

只支持简单单文件 old/new 文本替换。

scicodepilot/repair/repair_policy.py

确认边界：

RepairPolicy(require_confirmation=True, approved=False)

默认不 apply。

scicodepilot/repair/repair_runner.py

完整 repair workflow runner。

支持：

diagnosis
failure memory
patch plan
approval gate
optional patch apply
verification
restore original file
event stream
scicodepilot/eval/suite_runner.py

多任务 suite runner。

支持：

mode=diagnosis
mode=repair
confirm_apply=True/False
scicodepilot/backend/controller.py

M12 前端唯一推荐入口。

提供：

BackendController.list_tasks()
BackendController.get_task(task_id)
BackendController.run_task(task_id, mode, confirm_apply=False)
scicodepilot/backend/event_serializer.py

把 Pydantic event 转成 dict/json。

scicodepilot/backend/frontend_contract.md

前端接口说明。明确指出当前是同进程 asyncio event stream，不是 WebSocket；前端应使用 BackendController 和 serializer，不要直接调用内部 runner/tool。

5. Benchmark diagnosis demo 当前状态
当前 benchmark tasks
repair_tensor_shape_001

目的：

真实 PyTorch CPU tensor shape mismatch

核心错误：

classifier head expects 128 input features
upstream tensor has 64 features

入口命令：

python train.py

运行目录：

benchmark/tasks/repair_tensor_shape_001/repo

期望错误类型：

tensor_shape

期望最终：

diagnosis_passed: True
repair_dtype_mismatch_002

目的：

真实 PyTorch CPU dtype mismatch

核心错误：

float32 tensor 与 float64 tensor 做矩阵乘法

入口命令：

python train.py

运行目录：

benchmark/tasks/repair_dtype_mismatch_002/repo

期望错误类型：

dtype_mismatch

该任务文档说明它可以通过对齐 tensor dtype 修复，且运行在 CPU、不需要 CUDA。

repair_missing_module_003

目的：

Python 缺模块 / 环境依赖错误

核心错误：

ModuleNotFoundError
No module named definitely_missing_scicodepilot_dependency

入口命令：

python train.py

运行目录：

benchmark/tasks/repair_missing_module_003/repo

期望错误类型：

missing_module

该任务当前是 diagnosis-only，不生成 patch plan，因为缺依赖应由 EnvDoctor 处理，不应直接改 benchmark 脚本。

scripts/run_benchmark_diagnosis_demo.py

作用：

运行 repair_tensor_shape_001 的 diagnosis-only demo。

期望事件流包含：

[ErrorDetected] tensor_shape
[FailureMemoryCreated] tensor_shape
[TaskFinished] demo_finished

期望最终输出：

diagnosis_passed: True
已遇到问题：NumPy 缺失 warning 导致 parser 误判

真实 PyTorch 运行时曾遇到：

NumPy 缺失 warning / import warning

导致 stderr 中先出现类似缺依赖信息，parser 可能误判为：

missing_module

而不是最终的：

tensor_shape

解决方式：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
python -m pip install numpy

然后重跑：

python scripts/run_benchmark_diagnosis_demo.py

如果仍失败，应检查：

scicodepilot/tools/traceback_parser.py

重点：

parser 是否逐行扫描；
RuntimeError: mat1 and mat2 shapes cannot be multiplied 是否能被匹配；
规则优先级是否让真正 RuntimeError 优先于 warning；
如果 stderr 同时出现 warning 和 RuntimeError，应优先识别最终 RuntimeError；
必要时调整 ERROR_RULES 顺序或 parse 策略。

建议策略：

如果 stderr_lines 中存在明确 RuntimeError shape mismatch，优先返回 tensor_shape；
不要被前面的 warning / optional dependency message 抢先命中 missing_module。
6. 当前事件系统与前端展示建议

当前事件到 UI 的映射已写入 frontend_contract.md，前端应按照它消费事件。

事件	作用	前端展示建议
TaskStarted	任务开始	顶部标题、状态栏
PlanCreated	计划生成	左侧计划树
StepStarted	当前步骤开始	高亮当前步骤
CommandStarted	shell 命令开始	日志面板显示 $ command
CommandOutput	stdout/stderr 流式输出	日志面板；stdout/stderr 用不同样式
CommandFinished	命令结束	命令状态、return code
ErrorDetected	识别错误	右侧错误卡片
FailureMemoryCreated	结构化失败记忆	右侧 failure memory / reflection 卡片
PatchProposed	生成 patch plan	diff 面板
PatchApprovalRequired	需要用户确认	权限提示 / 确认按钮
PatchApplied	patch 已应用	patch 状态
VerificationStarted	验证开始	状态栏或验证区
VerificationFinished	验证结束	verification result
TaskFinished	任务结束	最终状态、summary
7. 当前重要命令清单
进入项目并激活环境
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
检查 Python / pip 路径
which python
which pip
python --version
python -m pip --version

确认路径应来自 scicodepilot-dev 环境。

安装 numpy

用于解决 PyTorch / NumPy warning 干扰诊断的问题：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
python -m pip install numpy
安装 CPU 版 torch

如果环境还没有 torch：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu

检查：

python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"

CPU 版看到：

False

是正常的。

运行所有测试
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
pytest -q

当前 M12 后期望：

51 passed

可能因后续修改而变化。

运行旧 backend demo
python scripts/run_backend_demo.py
运行 benchmark diagnosis demo
python scripts/run_benchmark_diagnosis_demo.py

期望：

diagnosis_passed: True
运行 repair demo：默认无确认
python scripts/run_benchmark_repair_demo.py

期望：

PatchProposed
PatchApprovalRequired
patch_applied: False
verification_success: False
运行 repair demo：显式确认 apply
python scripts/run_benchmark_repair_demo.py --confirm-apply

期望：

PatchApplied
VerificationFinished success=True

结束后仍应恢复原始 bug。

运行 benchmark suite：diagnosis
python scripts/run_benchmark_suite.py --mode diagnosis
运行 benchmark suite：repair 默认无确认
python scripts/run_benchmark_suite.py --mode repair
运行 benchmark suite：repair 显式确认
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
运行 frontend contract demo：默认 repair 无确认
python scripts/run_frontend_contract_demo.py
运行 frontend contract demo：missing module diagnosis
python scripts/run_frontend_contract_demo.py --task-id repair_missing_module_003 --mode diagnosis
运行 frontend contract demo：repair 显式确认
python scripts/run_frontend_contract_demo.py --task-id repair_tensor_shape_001 --mode repair --confirm-apply
确认 tensor shape benchmark 原始 bug 未被永久修复
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py

期望仍看到：

classifier_expected_dim = 128
classifier = nn.Linear(classifier_expected_dim, num_classes).to(device)
确认 dtype benchmark 原始 bug 未被永久修复
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py

期望仍看到：

dtype=torch.float64
8. 当前最重要的技术约定
所有运行都在 WSL Ubuntu 中执行。
项目根目录固定为：
/home/zengl/projects/SciCodePilot
Conda 环境固定为：
scicodepilot-dev
不要使用 Windows PowerShell 跑项目命令。
后端对前端只暴露：
BackendController
event_to_dict
event_to_json
前端不要直接依赖内部 runner/tool：
ShellTool
PatchApplier
PatchPlanner
RepairBenchmarkRunner
DiagnosisBenchmarkRunner

这一点已写入 frontend_contract.md。

事件流是前后端解耦核心。
当前 transport 是同进程 asyncio event stream，不是 WebSocket。后续如做 Web 版，可以在 BackendController.run_task(...) 外包一层 WebSocket wrapper。
mode="diagnosis" 表示只诊断，不修改代码。
注意不是 mode="diagnose"。如果新窗口或前端同学使用 diagnose，需要改成 diagnosis。
mode="repair" 默认只生成 patch plan，不 apply。
如果要真的 apply patch，必须：
confirm_apply=True

或者 CLI：

--confirm-apply
即使 apply patch，也必须在结束后恢复 benchmark 原始 bug。
benchmark task 必须可复现、可自动评分。
failure memory 必须结构化，不是普通自然语言反思。
missing_module 当前不生成 patch plan，后续应由 EnvDoctor 处理。
PyTorch benchmark 均应 CPU-only，不应依赖 CUDA/GPU。
9. 当前未完成内容与下一步建议
9.1 M13：前端联调检查清单 + 后端防坑补丁

下一步优先级最高。

目标不是继续大改后端，而是帮助前端同学把 Textual 接上：

Textual UI
→ BackendController.run_task()
→ async event stream
→ UI 面板实时刷新

建议 M13 做：

检查 BackendController.run_task() 在 Textual app 的 async 生命周期中是否好用；
检查事件字段是否够前端展示；
检查 PatchApprovalRequired 如何触发 UI 的确认按钮；
确认 UI 点击确认后是否重新以 confirm_apply=True 调用；
增加必要的后端防坑说明或小工具。
9.2 前后端联调还没做

当前只是后端提供了 frontend_contract.md 和 fake frontend demo。

真正 Textual UI 尚未接入。

前端同学需要实现：

任务选择
mode 选择
Run 按钮
日志面板
计划树
错误卡片
failure memory 卡片
diff 面板
确认 apply 按钮
状态栏
9.3 benchmark 任务数量还不够最终版

当前只有 3 个任务：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_missing_module_003

MVP 足够，但最终展示/报告建议扩到至少 6 个 demo tasks：

建议新增：

repair_missing_file_004
repair_entrypoint_error_005
repair_label_shape_006
9.4 hidden evaluator 还没完整实现

当前已有：

expected_diagnosis.json
diagnosis_evaluator
suite summary
results.jsonl
summary.json

但还没有正式 hidden evaluator：

evaluator/hidden_tests
score.json
workspace copy
外部评分流程

正式 benchmark 设计可继续做：

copy original task to temp workspace
agent modifies workspace
hidden evaluator runs
score.json generated
suite aggregates score
9.5 EnvDoctor 还没做

repair_missing_module_003 已能诊断 missing module，但不会修。

后续 EnvDoctor 可做：

读取 stderr
识别 ModuleNotFoundError
检查 requirements.txt / pyproject.toml
生成 environment repair plan
建议 pip install / conda install
可选验证 import

注意：环境修复需要更严格权限控制，不应默认执行安装命令。

9.6 LLM Planner / Fixer / Reviewer 还没做

当前 patch planning 是规则式，不是 LLM。

未来可以扩展：

Planner
Fixer
Reviewer
LLM tool calling
OpenHands SDK
LangGraph

但当前不建议立刻接。
先完成前端联调和更多 benchmark 更稳。

10. 当前完成度判断

当前后端 MVP 主逻辑已经完成。

可以这样定性：

MVP 后端核心逻辑已完成，可以交给前端联调。
最终版还需要补更多 benchmark、hidden evaluator、EnvDoctor、可选 LLM Planner/Fixer/Reviewer。

当前最适合做：

M13：前端联调检查清单 + 后端防坑补丁

或者如果前端还没开始：

扩展到 6 个 demo tasks

12. 最后备注

如在新窗口继续开发，建议第一步先运行：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
pytest -q
python scripts/run_frontend_contract_demo.py

确认当前基线稳定后，再做 M13。