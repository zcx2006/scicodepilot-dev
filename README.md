# SciCodePilot

**SciCodePilot: Memory-Augmented Structured Agent for Reliable Scientific Code Repair and Reproducibility**

SciCodePilot 是一个面向科研 Python / 机器学习代码诊断、修复与复现的结构化 Agent 原型系统。项目关注的核心问题是：当科研代码因为 tensor shape、dtype、device、loss input、collate function、配置键、缺失依赖或缺失数据文件等问题运行失败时，能否通过结构化失败记忆、相似案例检索、安全约束补丁生成和隔离验证，构建一个比直接根据 traceback 生成补丁更可审计、更安全、更可复现的修复流程。

本项目不会把 LLM 当作可以任意修改仓库的黑盒工具，而是把诊断、计划、审查、确认和验证拆成清晰的 pipeline。系统会先将失败转化为结构化 `FailureMemory`，再区分源码问题、环境问题和数据问题；只有通过安全审查并获得确认的补丁，才会在隔离 workspace 中应用和验证。

本仓库当前提供：

- 后端 Agent pipeline；
- internal controlled benchmark；
- Textual 终端前端；
- FastAPI 网页 homepage 与交互式 demo；
- FailureMemory retrieval；
- external repo smoke interface；
- LLM smoke 与结构化输出对比材料；
- 报告图表、实验表格和测试资产。

更完整的研究问题、方法设计、结果摘要、图表和交互式演示请运行网页 homepage。

## 快速开始

在已经 clone 本仓库并进入项目根目录后，安装依赖并启动网页：

```powershell
pip install -r requirements.txt
python scripts/run_web_demo.py
```

然后打开：

```text
http://127.0.0.1:8000
```

网页包含项目 homepage、侧边目录、研究方法说明、实验结果摘要、图表展示、external repo smoke 说明，以及可运行的 backend event-stream demo。

## 网页 Demo

网页 demo 使用 FastAPI + Server-Sent Events，将后端 `BackendController` 产生的事件流实时展示在浏览器中。页面中包含：

- 研究项目首页；
- 方法和实验结果说明；
- 多张报告图表；
- benchmark task 选择；
- diagnosis / repair 模式切换；
- FailureMemory、PatchPlan、Safety Review、Verification 卡片；
- 可复制的 timeline / transcript；
- 图片点击放大查看功能。

网页 demo 的目标是用于课堂展示、答辩录屏和组内演示。它不是生产级在线服务，默认以本地方式运行。

## GitHub Pages 静态主页

仓库同时提供了一个可用于 GitHub Pages 的静态项目主页：

```text
docs/index.html
```

该页面展示项目介绍、方法、benchmark、memory retrieval、LLM smoke、safety analysis、agent comparison、前端说明和运行方式。它不依赖 Python 后端，因此可以作为公开项目 homepage 发布。

启用方式：

1. 在 GitHub 仓库进入 `Settings`；
2. 打开 `Pages`；
3. Source 选择 `Deploy from a branch`；
4. Branch 选择包含该页面的分支；
5. Folder 选择 `/docs`；
6. 保存后等待 GitHub Pages 构建完成。

注意：GitHub Pages 是静态网页，不能在线运行 `Run / Confirm Apply`。真正的事件流 demo 仍需本地运行：

```powershell
python scripts/run_web_demo.py
```

## Textual 终端前端

项目也保留了 Textual 终端前端，可作为备用 demo 和开发调试入口：

```powershell
python scripts/run_textual_app.py
```

Textual smoke test：

```powershell
python scripts/run_textual_app.py --smoke-test
```

## Benchmark 运行

仅运行 diagnosis：

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

## External Repo Smoke

项目提供轻量级外部本地仓库 smoke 入口，用于验证系统不只依赖内置 benchmark task：

```powershell
python scripts/run_external_repo_smoke.py --repo-path <local_repo> --command "pytest -q" --mode diagnosis
```

该功能会复制外部仓库到 isolated workspace 中运行，不修改原始仓库。它的作用是检查外部入口、失败捕获、summary 输出和安全边界；它不是公开 benchmark，不是 BugsInPy / SWE-bench 结果，也不是 SOTA 对比。

## 主要目录

| 路径 | 说明 |
| --- | --- |
| `scicodepilot/backend/controller.py` | 前端使用的稳定后端入口 |
| `scicodepilot/frontend/web_demo/` | FastAPI homepage 与网页 demo |
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

推荐表述：

> SciCodePilot demonstrates a structured, safety-aware, and reproducible repair pipeline for controlled scientific Python failures.
