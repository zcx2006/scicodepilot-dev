# SciCodePilot

**SciCodePilot: Memory-Augmented Structured Agent for Reliable Scientific Code Repair and Reproducibility**

SciCodePilot 是一个面向科研 Python / 机器学习代码诊断、修复与复现的 structured agent 原型。系统将运行失败转化为结构化 `FailureMemory`，再进行错误路由、补丁计划、安全审查、人工确认和隔离验证。

本仓库当前提供：

- 后端 agent pipeline；
- internal controlled benchmark；
- Textual 终端前端；
- FastAPI 网页 homepage + demo；
- memory retrieval、external repo smoke、LLM smoke、报告图表和测试资产。

更完整的研究问题、方法、结果和交互式 demo 请运行网页 homepage。

## Quick Start

```powershell
cd C:\Users\user\Documents\scicodepilot\scicodepilot-dev
pip install -r requirements.txt
python scripts/run_web_demo.py
```

然后打开：

```text
http://127.0.0.1:8000
```

网页包含项目 homepage、侧边目录、研究方法说明、实验结果摘要、external repo smoke 说明，以及可运行的 backend event-stream demo。

## Textual Demo

保留的终端前端入口：

```powershell
python scripts/run_textual_app.py
```

Smoke test：

```powershell
python scripts/run_textual_app.py --smoke-test
```

## Benchmark Suite

Diagnosis：

```powershell
python scripts/run_benchmark_suite.py --mode diagnosis
```

Repair planning：

```powershell
python scripts/run_benchmark_suite.py --mode repair
```

Repair with confirmed apply：

```powershell
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

## External Repo Smoke

外部本地仓库 smoke 入口：

```powershell
python scripts/run_external_repo_smoke.py --repo-path <local_repo> --command "pytest -q" --mode diagnosis
```

该功能会复制外部仓库到 isolated workspace 中运行，不修改原始仓库。它是 smoke interface，不是公开 benchmark 或 SOTA 对比。

## Key Paths

| Path | Purpose |
| --- | --- |
| `scicodepilot/backend/controller.py` | 前端使用的稳定后端入口 |
| `scicodepilot/frontend/web_demo/` | FastAPI homepage 与网页 demo |
| `scicodepilot/frontend/textual_app.py` | Textual 终端前端 |
| `benchmark/tasks/` | internal controlled benchmark |
| `scripts/` | demo、benchmark、external smoke、导出脚本 |
| `docs/` | 架构、报告、答辩和交接文档 |
| `report_assets/` | 图表和实验表格 |
| `outputs/` | 运行结果、transcript 和实验输出 |

## Scope

SciCodePilot 目前应被表述为一个 controlled, auditable scientific-code repair prototype。当前结果主要支持 component-level analysis，不应声称完成 SWE-bench / BugsInPy，不应声称 SOTA，也不应把 external repo smoke 解释为公开 benchmark 性能。
