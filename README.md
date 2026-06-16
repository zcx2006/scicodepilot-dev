# SciCodePilot

**SciCodePilot: Memory-Augmented Structured Agent for Reliable Scientific Code Repair and Reproducibility**

SciCodePilot 是一个面向科研 Python / 机器学习代码诊断、修复与复现的结构化 Agent 原型系统。项目关注的核心问题是：当科研代码因为 tensor shape、dtype、device、loss input、collate function、配置键、缺失依赖或缺失数据文件等问题运行失败时，能否通过结构化失败记忆、相似案例检索、安全约束补丁生成和隔离验证，构建一个比直接根据 traceback 生成补丁更可审计、更安全、更可复现的修复流程。

本项目不会把 LLM 当作可以任意修改仓库的黑盒工具，而是把诊断、计划、审查、确认和验证拆成清晰的 pipeline。系统会先将失败转化为结构化 `FailureMemory`，再区分源码问题、环境问题和数据问题；只有通过安全审查并获得确认的补丁，才会在隔离 workspace 中应用和验证。

本仓库当前提供：

- 后端 Agent pipeline；
- internal controlled benchmark；
- FailureMemory retrieval；
- external repo smoke interface；
- LLM smoke 与结构化输出对比材料；
- FastAPI 网页 homepage 与交互式 demo；
- Textual 终端前端；
- 报告图表、实验表格和测试资产。

## 后端核心原理

SciCodePilot 的核心不是前端界面，而是一个面向科研代码失败的后端 Agent pipeline。它把一次运行失败拆成多个可记录、可审查、可复现的阶段：

```text
Run Command
  -> Parse Traceback
  -> Create FailureMemory
  -> Route Source / Environment / Data Failure
  -> Generate PatchPlan or EnvRepairPlan
  -> Safety Review
  -> Human Confirmation
  -> Apply in Isolated Workspace
  -> Verification
  -> Write Evidence / Transcript
```

与直接把 traceback 交给 LLM 生成补丁不同，本项目强调结构化中间状态。系统会先捕获 `stdout`、`stderr`、return code 和 traceback，再由 parser 提取错误类型与证据，生成 `FailureMemory`。这个 memory 记录的不只是报错文本，还包括 root cause hypothesis、repair action、运行命令和后续验证结果，因此可以用于审查、检索和复现实验。

后端还显式区分三类失败：

| 类型 | 示例 | 系统行为 |
| --- | --- | --- |
| 源码问题 | tensor shape、dtype、device、loss input、collate function、config key | 生成受约束 `PatchPlan` |
| 环境问题 | missing module、dependency error | 生成 `EnvRepairPlan`，不自动安装依赖 |
| 数据问题 | missing file、dataset path error | 提示数据/路径问题，不伪造数据文件 |

所有源码补丁都必须经过 `PatchSafetyReviewer`。通过审查后，系统仍需要显式确认，才会在 isolated workspace 中应用 patch 并重新运行 verification command。这个设计是为了避免 Agent 在科研代码中进行不可追踪、不可回滚或不应自动执行的修改。

## 后端模块

| 模块 | 位置 | 作用 |
| --- | --- | --- |
| BackendController | `scicodepilot/backend/controller.py` | 面向前端和 demo 的稳定后端入口，提供 task list 和 event stream |
| TracebackParser | `scicodepilot/tools/traceback_parser.py` | 从 stderr / traceback 中识别错误类型和证据 |
| FailureMemory | `scicodepilot/memory/` | 结构化保存失败、根因假设、修复动作和检索记录 |
| EnvDoctor | `scicodepilot/env/` | 处理缺依赖、缺文件等不应直接改源码的问题 |
| PatchPlanner | `scicodepilot/repair/` | 为可修复源码错误生成受约束 patch plan |
| PatchSafetyReviewer | `scicodepilot/review/` | 在应用补丁前检查路径、命令、依赖安装、benchmark mutation 等风险 |
| Workspace / Runner | `scicodepilot/eval/` | 复制任务到隔离 workspace，执行命令并保存验证结果 |
| Event schema | `scicodepilot/events/` | 将 TaskStarted、FailureMemoryCreated、PatchProposed 等阶段作为事件输出 |

后端事件流是前端展示和实验记录的基础。一次运行会产生类似 `TaskStarted`、`CommandStarted`、`ErrorDetected`、`FailureMemoryCreated`、`PatchProposed`、`PatchReviewCreated`、`PatchApplied`、`VerificationFinished`、`TaskFinished` 的事件。前端只是消费这些事件，核心诊断与修复逻辑仍然在后端。

## 快速开始

在已经 clone 本仓库并进入项目根目录后，安装依赖：

```powershell
pip install -r requirements.txt
```

运行 benchmark diagnosis：

```powershell
python scripts/run_benchmark_suite.py --mode diagnosis
```

生成 repair plan，但不确认应用 patch：

```powershell
python scripts/run_benchmark_suite.py --mode repair
```

确认应用 patch 并运行验证：

```powershell
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

## Benchmark 与实验资产

项目包含 10 个 internal controlled benchmark task，覆盖 tensor shape、dtype mismatch、device mismatch、loss input、collate function、config key、entrypoint、label shape、missing module 和 missing file 等科研代码常见失败类型。该 benchmark 的作用是进行 component-level evaluation，而不是作为公开 benchmark 或 SOTA 结果。

仓库中还包含：

- memory retrieval evaluation；
- safety stress cases；
- ablation tables；
- LLM smoke output；
- external repo smoke summaries；
- report-ready figures and tables；
- reproducibility and final defense documents。

这些资产主要用于说明各个组件是否按预期工作：parser 是否能识别失败，FailureMemory 是否结构化，EnvDoctor 是否避免错误源码 patch，PatchSafetyReviewer 是否拦截风险，verifier 是否能提供复现实验证据。

## External Repo Smoke

项目提供轻量级外部本地仓库 smoke 入口，用于验证系统不只依赖内置 benchmark task：

```powershell
python scripts/run_external_repo_smoke.py --repo-path <local_repo> --command "pytest -q" --mode diagnosis
```

该功能会复制外部仓库到 isolated workspace 中运行，不修改原始仓库。它的作用是检查外部入口、失败捕获、summary 输出和安全边界；它不是公开 benchmark，不是 BugsInPy / SWE-bench 结果，也不是 SOTA 对比。

## 前端展示

前端是后端事件流的展示层。项目目前提供两个前端入口：一个用于课堂展示和录屏的网页 demo，一个用于开发调试和备用演示的 Textual 终端前端。

启动本地网页 demo：

```powershell
python scripts/run_web_demo.py
```

然后打开浏览器：

```text
http://127.0.0.1:8000
```

网页 demo 使用 FastAPI + Server-Sent Events，将后端 `BackendController` 产生的事件流实时展示在浏览器中。页面包含：

- 研究项目首页；
- 方法和实验结果说明；
- 多张报告图表；
- benchmark task 选择；
- diagnosis / repair 模式切换；
- FailureMemory、PatchPlan、Safety Review、Verification 卡片；
- 可复制的 timeline / transcript。



## GitHub Pages 静态主页

仓库同时提供了一个可用于 GitHub Pages 的静态项目主页：

```text
[docs/index.html](https://zcx2006.github.io/scicodepilot-dev/)
```

该页面展示项目介绍、方法、benchmark、memory retrieval、LLM smoke、safety analysis、agent comparison、前端说明和运行方式。它不依赖 Python 后端，因此作为公开项目 homepage 发布。



```powershell
python scripts/run_web_demo.py
```

Textual 终端前端入口：

```powershell
python scripts/run_textual_app.py
```

Textual smoke test：

```powershell
python scripts/run_textual_app.py --smoke-test
```

## 主要目录

| 路径 | 说明 |
| --- | --- |
| `scicodepilot/backend/` | 前端和 demo 使用的后端入口与事件序列化 |
| `scicodepilot/memory/` | FailureMemory、memory record 和 retrieval store |
| `scicodepilot/repair/` | PatchPlan、PatchPlanner 和 PatchApplier |
| `scicodepilot/review/` | PatchSafetyReviewer 和 patch review schema |
| `scicodepilot/env/` | EnvDoctor 和 EnvRepairPlan |
| `scicodepilot/eval/` | benchmark runner、workspace、evaluator |
| `scicodepilot/frontend/web_demo/` | FastAPI homepage 与本地网页 demo |
| `scicodepilot/frontend/textual_app.py` | Textual 终端前端 |
| `benchmark/tasks/` | internal controlled benchmark |
| `scripts/` | demo、benchmark、external smoke、导出脚本 |
| `docs/` | 架构、报告、答辩和交接文档 |
| `report_assets/` | 图表和实验表格 |
| `outputs/` | 运行结果、transcript 和实验输出 |

## 项目边界

SciCodePilot 目前应被表述为一个 controlled、auditable 的科研代码修复原型系统。当前结果主要支持 component-level analysis，用于说明结构化 FailureMemory、路由机制、安全审查、隔离验证和前端可视化链路是否按预期工作。

需要避免的表述：

- 不声称完成 SWE-bench / BugsInPy；
- 不声称达到 SOTA；
- 不把 internal controlled benchmark 说成公开 benchmark；
- 不把 external repo smoke 说成真实泛化性能；
- 不声称系统会自动安装依赖或伪造缺失数据。


