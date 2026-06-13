# SciCodePilot GPT 设计交接文档：M23–M26

## 0. 用途

本交接文档用于在新的 GPT / Codex 对话中继续设计 SciCodePilot 的 M27 及后续工作。

当前上下文已经从 M1–M22 的后端系统构建，推进到 M23–M26 的报告资产、展示资产、public benchmark 规划、external repo smoke interface 和 component metrics。新 GPT 接手后，不应重复设计 M23–M26 已完成内容，也不应立刻盲目新增复杂功能，而应先理解当前系统的边界、已完成资产、前端未完成状态和后续最合理方向。

---

## 1. 项目基本信息

项目名：

```text
SciCodePilot
```

项目路径：

```bash
/home/zengl/projects/SciCodePilot
```

运行环境：

```text
WSL Ubuntu
Conda 环境：scicodepilot-dev
```

标准进入项目命令：

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev
```

长期约束：

```text
所有命令必须在 WSL Ubuntu 中运行。
不要在 Windows PowerShell 中运行项目命令。
涉及 Python / pip 时，优先使用当前 conda 环境中的 python / pip。
不要假设 ChatGPT Pro 等于 OpenAI API 可用。
不要把 API key 写入代码、文档、测试或 git。
```

当前最近一次完整测试结果：

```text
pytest -q: 157 passed in 49.62s
```

当前 WSL 运行时可能会打印一段 `localhost` / `WSL NAT` 相关乱码警告，但目前不影响命令成功执行。之前的 `Wsl/Service/E_ACCESSDENIED` 是 Codex sandbox 降级导致，不是项目代码问题；后来 Windows sandbox 恢复为 elevated，Codex workspace-write 后问题消失。

---

## 2. 当前项目定位

SciCodePilot 当前应被定义为：

```text
A structured failure-memory agent for reliable scientific code repair and reproducibility.
```

中文定位：

```text
面向可靠科研代码修复与复现的结构化失败记忆 Agent 系统。
```

它不是普通代码聊天机器人，也不是简单 API wrapper，而是一个事件流驱动的科研代码 diagnosis / repair / evaluation 后端系统。

当前核心链路：

```text
benchmark task or local repo command
→ run command
→ capture stdout/stderr/traceback
→ parse error
→ build structured FailureMemory
→ route source-code vs env/data failure
→ propose PatchPlan or EnvRepairPlan
→ PatchSafetyReviewer
→ optional confirmation
→ isolated workspace apply
→ verification
→ score.json / summary.json / manifest
→ event stream / report tables / demo assets
```

M0–M12 已经完成 EventBus、ShellTool、TracebackParser、FailureMemory、PatchPlan、PatchApplier、RepairPolicy、BenchmarkSuite、BackendController 和前端 contract 等后端主链路。

M13–M19 又完成了 benchmark 扩展、workspace isolation、hidden evaluator、EnvDoctor、Textual reference frontend、可选 LLM PatchPlanner、多 provider LLM adapter 和 PatchSafetyReviewer。

M20–M22 将项目从后端 demo 收束为研究型系统，补充 research questions、experiment protocol、failure taxonomy、safety cases、10-task controlled benchmark、ablation experiments 和 results analysis。

M23–M26 则主要完成报告资产、复现资产、public benchmark skeleton、showcase demo、external repo smoke interface 和 component metrics。

---

## 3. 必须保持的 public API

前端和外部调用只应依赖：

```python
from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json
```

`BackendController` public API 不要改：

```python
list_tasks()
get_task(task_id)
run_task(task_id, mode, confirm_apply=False)
```

`mode` 只能是：

```text
diagnosis
repair
```

不要改成：

```text
diagnose
```

前端同学、文档网站、Textual reference frontend 都应围绕这个接口，不要直接调用内部 runner、tool、PatchPlanner、PatchApplier、EnvDoctor、suite runner 或 external smoke 脚本。

---

## 4. 当前团队状态

当前小组状态：

```text
用户本人负责后端。
前端同学还没有真正开始做她的部分。
```

已有一个 M16 的 Textual reference frontend，但这只是 reference frontend，不等于前端同学已经完成最终展示界面。后续不要把项目成功依赖在复杂前端上。应该保留后端 showcase script、demo transcript、Mermaid 图、report tables 和命令行 demo 作为兜底展示方案。

如果前端同学开始做，建议她只做轻量展示：

```text
Task list
Event stream
FailureMemory card
PatchPlan / PatchReview card
EnvRepairPlan card
Verification result
Reproducibility manifest link
```

不要让前端同学：

```text
重写 BackendController
直接调用内部 runner/tool
引入数据库
做复杂 web dashboard
依赖真实 API key
依赖 public benchmark 下载
```

---

## 5. 当前 benchmark 与实验边界

当前 internal controlled benchmark 共 10 个 task：

| Task | Error Type | Category |
|---|---|---|
| `repair_tensor_shape_001` | `tensor_shape` | source-code repair |
| `repair_dtype_mismatch_002` | `dtype_mismatch` | source-code repair |
| `repair_missing_module_003` | `missing_module` | env/data routing |
| `repair_missing_file_004` | `missing_file` | env/data routing |
| `repair_entrypoint_error_005` | `entrypoint_error` | source-code repair |
| `repair_label_shape_006` | `label_shape` | source-code repair |
| `repair_device_mismatch_007` | `device_mismatch` | source-code repair |
| `repair_loss_input_008` | `loss_input_error` | source-code repair |
| `repair_collate_fn_009` | `collate_fn_error` | source-code repair |
| `repair_config_key_010` | `config_key_error` | source-code repair |

当前结果必须表述为：

```text
internal controlled benchmark
component-level evaluation
not a public benchmark
not a SOTA comparison
```

不要说：

```text
SciCodePilot achieves SOTA.
SciCodePilot outperforms SWE-agent / mini-swe-agent / AutoCodeRover.
SciCodePilot completed BugsInPy evaluation.
SciCodePilot completed SWE-bench evaluation.
average_score=1.0 proves real-world generalization.
Mock LLM repair represents real LLM performance.
```

M24 的 final report draft 已明确：当前报告评估的是 internal 10-task controlled benchmark，不是 public benchmark，也不是 SOTA comparison；当前 evidence 只支持 pipeline 在项目约束下解决 designed controlled tasks，不证明 public bug benchmark 或 issue-level repair 能力。

---

## 6. M23–M26 总览

### M23A：Final Report Assets and Reproducibility Manifest

目标：

```text
固定当前内部实验资产，生成复现 manifest 和报告基础文档。
```

完成内容：

```text
scripts/export_repro_manifest.py
docs/reproducibility.md
docs/internal_ablation_v2.md
docs/report_outline.md
report_assets/figures/event_flow.md
report_assets/figures/system_pipeline.md
tests/test_repro_manifest.py
report_assets/tables/repro_bundle_manifest.md
artifacts/repro_bundle/20260523_195337/manifest.md
```

验证结果：

```text
export_repro_manifest.py 运行成功
Missing files: none
pytest -q: 139 passed in 44.17s
```

关键意义：

```text
把实验结果绑定到 repro bundle、git commit、环境信息、Python/conda/pip/GPU/Docker 信息。
报告里可以说 internal controlled experiments 有复现证据链。
```

注意：

```text
M23A 不改变核心后端。
M23A 不接 public benchmark。
M23A 不声称 SOTA。
```

---

### M23B：Public Benchmark Pilot Planning and Adapter Skeleton

目标：

```text
为未来接入 public benchmark 做轻量 metadata skeleton，不真正下载或运行 BugsInPy / SWE-bench。
```

完成内容：

```text
docs/public_benchmark_plan.md
docs/public_benchmark_adapter.md
scicodepilot/benchmarks/__init__.py
scicodepilot/benchmarks/public_task.py
scicodepilot/benchmarks/public_registry.py
scripts/list_public_pilot_tasks.py
tests/test_public_benchmark_adapter.py
```

验证结果：

```text
python scripts/list_public_pilot_tasks.py
pytest -q: 144 passed in 40.25s
```

当前 public benchmark adapter 是 metadata-only skeleton。它不下载仓库、不安装依赖、不运行 benchmark test、不报告 completed public benchmark results。文档已明确不能将其写成 SWE-bench / BugsInPy / external baseline comparison。

public benchmark plan 当前推荐顺序：

```text
1. BugsInPy-style pilot
2. SWE-bench Lite small subset
3. external baseline comparison
```

但当前阶段不能声称已经完成这些结果。

---

### M24：Final Report Draft Pack

目标：

```text
生成最终报告草稿资产，先把报告主线写出来。
```

完成内容：

```text
docs/final_report_draft.md
docs/report_claims_checklist.md
docs/table_and_figure_inventory.md
docs/demo_story.md
tests/test_report_assets.py
```

验证结果：

```text
pytest -q: 149 passed in 41.29s
```

关键内容：

```text
final_report_draft.md
report_claims_checklist.md
table_and_figure_inventory.md
demo_story.md
```

claim 检查已经避免：

```text
state-of-the-art
outperforms SWE-agent
completed SWE-bench
completed BugsInPy
```

报告草稿当前主线：

```text
SciCodePilot demonstrates a structured failure-memory approach to reliable scientific code repair and reproducibility on an internal controlled benchmark.
```

不能把报告写成：

```text
public benchmark result
SOTA comparison
real-world generalization proof
```

---

### M25：Showcase and Demo Polish Pack

目标：

```text
让项目更适合答辩展示和报告呈现，而不是继续堆后端功能。
```

完成内容：

```text
scripts/run_showcase_demo.py
docs/demo_transcript.md
docs/contribution_comparison.md
report_assets/figures/benchmark_distribution.md
tests/test_showcase_assets.py
```

验证命令：

```bash
command -v mmdc || true
python scripts/run_showcase_demo.py
pytest -q
```

验证结果：

```text
pytest -q: 154 passed in 48.63s
```

showcase demo 当前展示：

```text
repair_tensor_shape_001 diagnosis
FailureMemory
repair without apply 的 PatchProposal / PatchReview
confirm apply 后的 verification
repair_missing_module_003 的 EnvRepairPlan
4 个 safety stress case 摘要
reproducibility manifest
report figures
```

环境中没有 `mmdc`，所以没有生成 SVG；保留 Markdown / Mermaid source。

M25 的意义：

```text
解决“只看到 pytest 和 10-task 结果不出彩”的展示问题。
让答辩能通过一条命令展示完整 agent pipeline。
```

---

### M26：External Repo Smoke Test Pack

目标：

```text
让 SciCodePilot 不只看起来能跑内置 benchmark/tasks，而是具备对任意本地 Python repo 做 smoke diagnosis / repair planning 的入口。
```

完成内容：

```text
scripts/run_external_repo_smoke.py
scripts/export_component_metrics.py
docs/external_repo_smoke_test.md
report_assets/tables/component_metrics.md
tests/test_external_repo_smoke.py
tests/test_component_metrics.py
```

修改内容：

```text
docs/final_report_draft.md
docs/table_and_figure_inventory.md
```

验证命令：

```bash
python scripts/run_external_repo_smoke.py --help
python scripts/export_component_metrics.py --latest
pytest -q
```

验证结果：

```text
pytest -q: 157 passed in 49.62s
```

external repo smoke 用法：

```bash
python scripts/run_external_repo_smoke.py --repo-path /path/to/repo --command "pytest -q"
python scripts/run_external_repo_smoke.py --repo-path /path/to/repo --command "pytest -q" --mode repair-plan
```

它会复制 repo 到：

```text
outputs/external_smoke/<timestamp>/workspace
```

并生成：

```text
outputs/external_smoke/<timestamp>/summary.md
outputs/external_smoke/<timestamp>/summary.json
```

默认：

```text
不 apply patch
不修改原始 repo
不绕过 PatchSafetyReviewer
不下载 public benchmark
不接 external baseline
```

external smoke 文档明确说明：这是 lightweight smoke interface，不是 public benchmark，不是 SOTA comparison，也不是 BugsInPy / SWE-bench replacement。

M26 已在 final report draft 中加入 `External Repo Smoke Interface` 小节，明确它只是 smoke tool，不下载 BugsInPy / SWE-bench、不运行 external baselines、不对原始 repo apply patch。

---

## 7. 当前报告与展示资产

当前 table / figure inventory 已包含：

Tables：

```text
report_assets/tables/ablation_table.md
report_assets/tables/safety_table.md
report_assets/tables/repro_bundle_manifest.md
report_assets/tables/component_metrics.md
```

Figures：

```text
report_assets/figures/event_flow.md
report_assets/figures/system_pipeline.md
```

Supporting docs：

```text
docs/research_questions.md
docs/experiment_protocol.md
docs/failure_taxonomy.md
docs/safety_cases.md
docs/internal_ablation_v2.md
docs/reproducibility.md
docs/external_repo_smoke_test.md
docs/public_benchmark_plan.md
docs/public_benchmark_adapter.md
```

当前 inventory 认为这些资产已经 ready，但表格 caption 和 Mermaid visual styling 仍可人工润色。

---

## 8. 当前 component metrics 注意事项

M26 生成的：

```text
report_assets/tables/component_metrics.md
```

当前内容显示：

```text
total controlled tasks: 10
diagnosis pass count: 0
patch plan count: 8
env repair plan count: 2
patch review count: 8
patch applied count: 8
verification success count: 8
scored task count: 8
average score: 1.0
safety stress case pass count: 10
```

其中 `diagnosis pass count: 0` 需要新 GPT / Codex 后续特别注意。

这可能不是系统诊断失败，而是 `export_component_metrics.py` 从 `full_rule_based_repair` 或 ablation summary 的某个 repair variant 中读取字段时，诊断计数没有被该 variant 记录。M22 交接中明确 diagnosis suite 曾经是：

```text
total_tasks=10
diagnosis_pass_count=10
```

所以后续写报告或做表时，不能直接把 component_metrics 里的 `diagnosis pass count: 0` 解释成系统诊断失败。建议 M27/M28 之前先检查 `export_component_metrics.py` 的语义：它应该区分 diagnosis-only variant 和 full repair variant，或者在表格里标注 `not recorded in this variant`，避免报告数字自相矛盾。

---

## 9. 当前核心贡献应如何表述

建议最终报告和答辩用以下 4 个贡献点：

### Contribution 1：Structured FailureMemory

`FailureMemory` 是科研代码失败的结构化中间表示。

它将：

```text
traceback
stdout/stderr
command
error evidence
root cause hypothesis
repair action
context summary
```

转化为可路由、可审查、可验证的 agent state。

后续 M27 如果做 memory retrieval，则应进一步升级为：

```text
可检索的 historical FailureMemory
top-k similar failure cases
ICL examples for LLM PatchPlanner
successful/failed verification result write-back
```

---

### Contribution 2：Source / Environment / Data Routing

系统通过 EnvDoctor 区分：

```text
source-code repair
environment dependency issue
missing data / file issue
```

核心原则：

```text
missing_module → EnvRepairPlan，不自动 pip install
missing_file → EnvRepairPlan，不创建假文件
source-code failure → PatchPlan
```

这避免把 missing dependency / missing data 错误地修成代码 patch。

---

### Contribution 3：Safety-Constrained Patch Planning and Isolated Verification

无论 patch 来自：

```text
rule-based PatchPlanner
mock LLM Planner
future real LLM Planner
future retrieved-memory LLM Planner
```

都必须经过：

```text
PatchSafetyReviewer
PatchReviewCreated
optional user confirmation
isolated workspace apply
verification
score.json / summary.json / manifest
```

PatchSafetyReviewer 会阻断危险 pattern，例如：

```text
absolute path
../ path traversal
benchmark path modification
outputs modification
tests modification
requirements.txt / pyproject.toml
pip install / conda install
rm -rf
sudo
os.system
subprocess
eval
exec
multi-file unsafe diff
```

---

### Contribution 4：Controlled Evaluation + Ablation + Safety + Reproducibility

当前 internal controlled benchmark 的作用是 component-level evaluation，而非 public SOTA benchmark。

建议准备以下报告表：

```text
表 1：Internal benchmark total result
表 2：Error family statistics
表 3：Ablation
表 4：Safety stress cases
表 5：External repo smoke tests
表 6：LLM / memory-augmented planner cost and reliability，若 M27 后实现
```

---

## 10. 当前最重要的研究主线

之前讨论后，建议将项目主线从：

```text
We build a scientific code repair agent.
```

升级为：

```text
We study whether memory-augmented structured repair agents can improve the safety, interpretability, and reproducibility of scientific Python/ML code repair compared with direct LLM patching.
```

中文：

```text
我们研究结构化 FailureMemory 是否能提升科研代码修复 Agent 的安全性、可解释性和复现性。系统将每次失败转化为可检索的 memory，并通过相似错误检索、ICL patch planning、环境/数据/源码路由、安全审查和隔离验证形成闭环。
```

理想 agent loop：

```text
New failure
→ TracebackParser
→ FailureMemory
→ retrieve top-k similar FailureMemory cases
→ construct ICL prompt
→ LLM proposes structured PatchPlan JSON
→ PatchSafetyReviewer
→ isolated verification
→ successful/failed case written back to memory
```

这能更好对应课程要求中的：

```text
Agent
memory
retrieval
ICL
LLM
tool use
feedback
self-improvement
evaluation
safety
reproducibility
```

---

## 11. 已讨论但尚未实现的方向

以下内容在当前对话中已经讨论过，但截至 M26 **尚未实现**，不能写成已完成结果。

### 11.1 FailureMemory Retrieval

尚未实现：

```text
historical FailureMemory store
similarity retrieval
top-k memory examples
retrieved cases as ICL prompt
verification result write-back
```

这是 M27 最推荐方向之一，因为它能让 FailureMemory 从“结构化记录”升级为“真正 memory”。

---

### 11.2 Real LLM Structured PatchPlan Comparison

已有：

```text
optional LLM PatchPlanner adapter
multi-provider LLM support: mock / deepseek / gemini / openai / disabled
mock LLM repair path
```

但尚未系统评测真实 provider。

尚未实现正式对比：

```text
Rule-only planner
Direct LLM patch
LLM structured PatchPlan
Retrieved FailureMemory + LLM structured PatchPlan
```

如果 M27/M28 做 LLM，应保持：

```text
LLM 只输出受约束 PatchPlan JSON
LLM 不直接改文件
LLM 不执行 shell
LLM 不安装依赖
LLM patch 仍过 PatchSafetyReviewer
LLM 失败 fallback 到 rule-based planner
```

---

### 11.3 Direct LLM Patch Baseline

尚未实现。

如果实现，建议作为 analysis baseline，只允许在 sandbox / copied workspace 里生成 patch proposal，不允许绕过 reviewer，不允许直接污染 benchmark 原始 repo。

目标不是证明 direct LLM 最强，而是分析：

```text
direct free-form patch 是否更危险
structured PatchPlan 是否更可审查
retrieved FailureMemory 是否能改善 planning quality
```

---

### 11.4 LoRA / 小模型微调

尚未实现，也不建议作为主线。

可以作为 optional extension：

```text
traceback + command + file context → failure type classifier
```

但当前数据规模太小，不适合强行做 CNN/LSTM/LoRA 作为主贡献。除非课程明确要求必须有模型训练，否则不要让它破坏主线。

---

### 11.5 Inference / Cost / Reliability Analysis

尚未实现。

如果 M27/M28 接真实 LLM，可以增加表：

| Setting | Tokens | Latency | Cost | Success | Unsafe patch |
|---|---:|---:|---:|---:|---:|
| Direct LLM patch | TBD | TBD | TBD | TBD | TBD |
| Structured PatchPlan | TBD | TBD | TBD | TBD | TBD |
| Rule + LLM fallback | TBD | TBD | TBD | TBD | TBD |
| Retrieved memory + LLM | TBD | TBD | TBD | TBD | TBD |

---

## 12. M27 最推荐方向

虽然本交接文档不继续详细设计新功能，但为了新 GPT 能接上上下文，记录当前最合理的 M27 方向：

```text
M27: FailureMemory Retrieval and Memory-Augmented Planning Pack
```

原因：

```text
1. 课程要求强调 Agent、memory、retrieval、ICL、feedback、自我改进。
2. 当前 FailureMemory 还主要是结构化记录，不是真正 retrieval memory。
3. 这个方向不会推翻 M1–M26，能自然增强已有系统。
4. 它比继续增加 toy benchmark 更能提升创新性。
5. 它比强行做 CNN/LSTM/LoRA 更贴合当前项目。
```

M27 的合适范围应是：

```text
实现一个轻量 FailureMemoryStore
从 internal benchmark successful cases 导出 memory records
支持 top-k similarity retrieval，先可用关键词/Jaccard/简单 embedding-free 方法
为 LLM structured PatchPlanner 构造 ICL prompt
提供 mock LLM / offline tests
不要求真实 API key
不改变 BackendController public API
不改变 benchmark 主路径默认行为
```

M27 不应做：

```text
大规模 SWE-bench
大规模 BugsInPy
OpenHands
LangGraph
复杂 agent graph
默认启用真实 LLM
直接让 LLM 改文件
自动 pip install
自动创建 missing file
```

---

## 13. M28 / M29 可能方向

### M28：Real LLM Structured Planner Smoke Test

前提：

```text
M27 已经有 memory retrieval / ICL prompt construction。
```

目标：

```text
用 DeepSeek / Gemini / OpenAI 中一个真实 provider 做 3 个 internal task smoke test。
比较 rule-only、structured LLM、retrieved-memory structured LLM。
记录 tokens / latency / cost / invalid JSON / safety review / verification。
```

必须保持：

```text
不作为主 benchmark claim。
不声称真实 LLM 泛化。
不声称 SOTA。
不绕过 PatchSafetyReviewer。
```

---

### M29：Presentation / Frontend Fallback Pack

目标：

```text
如果前端同学仍未完成，准备完全不依赖前端的最终答辩材料。
```

内容：

```text
PPT outline
demo screenshots
terminal demo script
frontend fallback screenshots
system architecture SVG/PNG
event flow SVG/PNG
failure memory card mockup
patch review card mockup
EnvRepairPlan card mockup
```

这很重要，因为当前前端同学还没开始，不能把最终展示押在她那边。

---

## 14. 不建议后续做什么

不要继续盲目扩展 benchmark 到 20/30 个 controlled tasks。边际收益低，仍会被质疑是自建 toy benchmark。

不要现在大规模跑 SWE-bench / BugsInPy。环境成本高，容易拖垮报告和 demo。

不要强行做 CNN/LSTM 修代码。当前数据规模和任务形态不匹配，容易显得为了套课程名词而偏题。

不要把 LLM planner 变成默认主路径。默认主路径必须可复现、离线可跑、无 API key 也能 demo。

不要修改 BackendController public API。前端和文档围绕它建立。

不要让 EnvDoctor 自动 pip install / conda install。

不要让 EnvDoctor 创建 missing file 或假数据。

不要让 patch 修改 benchmark 原始 repo。

不要绕过 PatchSafetyReviewer。

不要把 external repo smoke test 写成 public benchmark result。

不要把 component_metrics 里有歧义的 `diagnosis pass count: 0` 直接放进最终报告而不解释。

---

## 15. 当前建议书主线

项目建议书建议使用这一版核心表述：

```text
本项目的核心假设是：在科研 Python / ML 代码修复中，相比直接由 LLM 根据 traceback 生成补丁，先将失败转化为结构化 FailureMemory，并显式区分源码、环境和数据问题，再经过相似 memory 检索、ICL patch planning、安全审查与隔离验证，可以提升修复流程的可审计性、安全性和复现性，同时避免将不可修复或不应自动修复的问题错误地转化为代码补丁。
```

建议贡献点：

```text
1. FailureMemory as structured and retrievable agent state
2. Source / environment / data failure routing
3. Safety-constrained PatchPlan generation and isolated verification
4. Controlled benchmark + ablation + safety stress cases + external smoke evaluation framework
```

建议实验表：

```text
Table 1: Internal benchmark total results
Table 2: Error-family statistics
Table 3: Ablation
Table 4: Safety stress cases
Table 5: External repo smoke tests
Table 6: LLM / memory retrieval cost and reliability，若 M27/M28 完成
```

---

## 16. 当前重要命令清单

进入项目：

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev
```

完整测试：

```bash
pytest -q
```

当前期望：

```text
157 passed
```

diagnosis suite：

```bash
python scripts/run_benchmark_suite.py --mode diagnosis
```

repair without apply：

```bash
python scripts/run_benchmark_suite.py --mode repair
```

repair with confirm apply：

```bash
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
```

mock LLM repair：

```bash
SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
```

M20 experiment pack：

```bash
python scripts/run_experiments.py --quick
python scripts/export_results_table.py --latest
```

M22 ablation pack：

```bash
python scripts/run_ablation_experiments.py --quick --include-safety
python scripts/export_ablation_tables.py --latest
```

M23A repro manifest：

```bash
python scripts/export_repro_manifest.py --bundle-dir artifacts/repro_bundle/20260523_195337
```

M23B public pilot list：

```bash
python scripts/list_public_pilot_tasks.py
```

M25 showcase：

```bash
python scripts/run_showcase_demo.py
```

M26 external repo smoke：

```bash
python scripts/run_external_repo_smoke.py --repo-path /path/to/repo --command "pytest -q"
python scripts/run_external_repo_smoke.py --repo-path /path/to/repo --command "pytest -q" --mode repair-plan
```

M26 component metrics：

```bash
python scripts/export_component_metrics.py --latest
```

原始 benchmark 污染检查：

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

---

## 17. 新 GPT 接手后的第一步

新 GPT / Codex 接手后，第一步不要设计新功能。先做：

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev
git status
pytest -q
```

然后检查：

```bash
python scripts/run_showcase_demo.py
python scripts/export_component_metrics.py --latest
python scripts/run_external_repo_smoke.py --help
```

再检查当前 M23–M26 是否已经 git commit。不要假设所有新增文件都已提交。若未提交，建议先提交稳定状态：

```bash
git status
git add <M23-M26 changed files>
git commit -m "Add report assets, showcase, and external smoke interface"
```

---

## 18. 新 GPT 的接续建议

新 GPT 可以这样开场：

```text
我已经阅读 SciCodePilot M1–M26 交接文档。当前系统已经完成 internal controlled benchmark、ablation、safety review、reproducibility manifest、public benchmark skeleton、showcase demo 和 external repo smoke interface。当前 pytest 期望为 157 passed。前端同学尚未完成前端，因此后续设计必须保留 terminal demo 和 report assets 兜底。下一步不要重复做 M23–M26，也不要大规模跑 public benchmark。优先考虑 M27: FailureMemory Retrieval and Memory-Augmented Planning Pack，并保持 BackendController public API 不变。
```

---

## 19. 最重要的提醒

当前项目不是“只有 10 个 toy bug 的修复脚本”。

更准确的定位是：

```text
一个围绕科研代码修复构建的 agentic evaluation backend：
有事件流、
有 FailureMemory、
有 env/data/source routing、
有 safety review、
有 workspace isolation、
有 ablation、
有 reproducibility manifest、
有 external repo smoke interface、
有 showcase demo、
有 final report draft。
```

后续 M27 最需要补的是：

```text
让 FailureMemory 从结构化记录升级成可检索 memory，
让 LLM planning 从 mock path 升级成受约束、可比较、可审查的 structured PatchPlan 实验。
```

但在任何后续设计中，都必须继续守住：

```text
not public benchmark unless actually run
not SOTA unless actually compared
not direct unsafe patching
not original repo mutation
not API-key-dependent demo
not breaking BackendController
```
