# Textual 前端更新说明

## 概述

本次更新是在项目原有 Textual reference frontend 的基础上做的前端增强。原来的前端已经可以选择任务、运行 diagnosis / repair 模式，并把后端事件打印到几个日志面板中。本次改动的目标是把它升级成更适合课堂展示和答辩说明的 SciCodePilot Agent 运行控制台。

一句话总结：

```text
从“能跑事件日志”升级为“能展示 Agent 诊断、记忆、补丁、安全审查和验证流程”的前端界面。
```

## 涉及文件

- `scicodepilot/frontend/textual_app.py`
  - Textual 前端主文件，本次主要改动都在这里。
- `requirements.txt`
  - 新增基础依赖说明，包括 `textual`。
- `.gitignore`
  - 忽略 Python 缓存、workspace 输出和前端日志输出。

## 主要改动

### 1. 增加 Execution Plan Tree

新增了中间区域的 `Execution Plan` 树，用来展示后端计划和当前执行进度。

示例：

```text
[x] 1. Run command
[x] 2. Parse failure
[x] 3. Build memory
[ ] 4. Generate patch
```

需要注意的是，后端在 `diagnosis` 模式下并不是每个逻辑步骤都会发出 `StepStarted` 事件。因此前端增加了事件到步骤的映射逻辑：

- `CommandFinished` -> 命令执行步骤完成
- `ErrorDetected` -> 错误解析步骤完成
- `FailureMemoryCreated` -> FailureMemory 生成步骤完成
- `TaskFinished` -> 评估 / 最终步骤完成

这部分只是前端逻辑，没有修改后端代码。

### 2. 增加 Run Summary 面板

右侧新增了 `Run Summary` 面板，用来概括当前运行结果：

```text
Task
Command
Error
Memory
Plan
Review
Apply
Verify
Final
Transcript
```

这个面板的作用是方便展示和截图。观众不需要读完整日志，也能快速知道这一轮运行发生了什么。

### 3. 结构化展示后端事件

右侧区域现在按 SciCodePilot 的核心流程拆分：

```text
Diagnosis and Memory
Repair and Verification
```

其中 `Diagnosis and Memory` 主要展示：

- Error Card
- FailureMemory Card
- EnvRepairPlan Card

`Repair and Verification` 主要展示：

- Plan Card
- Patch Card
- Safety Review Card
- Confirmation Card
- Apply Card
- Verification Card
- Task Summary Card

这样更贴合项目主线：

```text
error -> FailureMemory -> PatchPlan / EnvRepairPlan -> review -> apply -> verify
```

### 4. 增加可复制 transcript 导出

Textual 终端界面里的文字不一定方便复制，所以本次更新增加了自动导出功能。

每次运行任务后，前端会在下面目录生成一份可复制文本：

```text
outputs/frontend_logs/
```

示例文件名：

```text
20260613_015418_repair_collate_fn_009_diagnosis_transcript.txt
```

这份 transcript 会按事件顺序记录本次运行过程，适合发给组员、放入报告或作为 demo 记录。

### 5. 视觉样式调整

本次还做了若干 UI 样式调整：

- 三栏布局：左侧控制区，中间计划树和日志，右侧结构化结果。
- 所有主要面板改为圆角边框。
- 统一蓝色边框。
- 使用橙色小标题。
- 统一面板背景色。
- Task / Mode 选择框改为和其他面板一致的圆角样式。
- Status 移到左侧顶部，方便查看当前状态。

## 如何运行

进入项目根目录：

```powershell
cd C:\Users\user\Documents\scicodepilot\scicodepilot-dev
```

运行 Textual 前端：

```powershell
python scripts\run_textual_app.py
```

如果缺少依赖：

```powershell
pip install -r requirements.txt
```

运行 smoke test：

```powershell
python scripts\run_textual_app.py --smoke-test
```

## 当前后端接口

前端仍然只使用后端提供的公开接口：

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict
```

核心调用：

```python
controller.list_tasks()
controller.run_task(task_id, mode, confirm_apply=False)
```

前端没有直接调用内部模块，例如：

```text
PatchPlanner
PatchApplier
RepairBenchmarkRunner
DiagnosisBenchmarkRunner
EnvDoctor
```

这些仍然属于后端内部逻辑。

## 当前支持范围

当前 UI 支持的是项目内部 benchmark tasks，也就是：

```text
benchmark/tasks/
```

目前还不支持在 UI 中输入任意外部仓库路径和命令，例如：

```text
repo_path
command
```

原因是后端目前没有向前端暴露稳定的 external repo 运行接口。如果后续要支持外部仓库，需要后端新增类似接口：

```python
run_external_smoke(repo_path, command)
```

并且最好继续返回和当前内部 benchmark 一致的 event stream。

## 给组员 / Reviewer 的说明

- 原项目中已经存在一个基础 Textual frontend。
- 本次工作不是从零写前端，而是在原有前端基础上做 UI/UX 和展示逻辑增强。
- 后端 pipeline 没有被重写。
- 前端新增的 Execution Plan Tree 通过后端事件推断阶段进度。
- diagnosis 模式下后端不是每一步都发 `StepStarted`，所以前端补充了事件到步骤的映射。
- 前端运行生成的 transcript 和日志会放到 `outputs/frontend_logs/`，并通过 `.gitignore` 忽略。

## 当前价值

这个前端现在可以比较完整地展示 SciCodePilot 的核心流程：

```text
选择任务
运行原始命令
捕获错误
生成 FailureMemory
生成 EnvRepairPlan 或 PatchPlan
进行安全审查
等待用户确认
应用补丁
重新验证
生成运行总结和 transcript
```

它适合用作 internal benchmark 的 demo frontend，也适合课堂展示、答辩录屏和实验过程说明。

