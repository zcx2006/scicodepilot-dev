# SciCodePilot GPT 设计交接文档：M27–M29

## 0. 用途

本交接文档用于在新的 GPT / Codex 对话中继续设计 SciCodePilot 的 M30、最终答辩材料、PPT、前端同学对接材料和后续收尾工作。

当前项目已经从 M1–M26 的后端系统、报告资产、showcase demo、external repo smoke interface，继续推进到 M27–M29 的 FailureMemory retrieval、memory retrieval evaluation 和 final defense integration。新 GPT 接手后，不应重复设计 M27–M29 已完成内容，也不应立刻盲目新增复杂功能。当前最重要的是：保持系统边界清晰，准备答辩，避免 overclaim。

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

当前最近一次完整测试结果：

```text
pytest -q: 181 passed in 48.23s
```

不要在代码或测试中硬编码这个测试数量。它只是当前已知状态。

长期约束：

```text
所有项目命令必须在 WSL Ubuntu 中运行。
不要在 Windows PowerShell 中运行项目命令。
Python / pip 优先使用 scicodepilot-dev 环境中的 python / pip。
不要假设 ChatGPT Pro 等于 OpenAI API 可用。
不要把 API key 写入代码、文档、测试或 git。
不要为了展示而下载 public benchmark 或真实大模型依赖。
```

---

## 2. 当前项目定位

SciCodePilot 当前应被定义为：

```text
A structured failure-memory agent for reliable scientific Python/ML code repair and reproducibility.
```

中文定位：

```text
面向可靠科研 Python / ML 代码修复与复现的结构化失败记忆 Agent 系统。
```

更适合答辩的一句话：

```text
SciCodePilot 不是直接让 LLM 根据 traceback 改代码，而是把失败转成结构化 FailureMemory，先区分源码、环境和数据问题，再经过 PatchPlan / EnvRepairPlan、安全审查、隔离验证和复现记录；M27/M28 又把 FailureMemory 扩展成可检索 memory，用于未来 memory-augmented structured planning。
```

当前系统不是：

```text
普通代码聊天机器人
简单 API wrapper
SWE-bench 解题系统
SOTA 自动程序修复系统
真实 LLM patch benchmark
```

当前系统是：

```text
一个围绕科研代码修复构建的 agentic evaluation backend：
有事件流、
有 FailureMemory、
有 source/env/data routing、
有 safety review、
有 workspace isolation、
有 internal controlled benchmark、
有 ablation、
有 reproducibility manifest、
有 external repo smoke interface、
有 deterministic FailureMemory retrieval、
有 retrieval evaluation、
有 final defense assets。
```

---

## 3. 必须保持的 public API

前端同学和外部展示应只依赖：

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

M27–M29 都没有修改 `BackendController` public API。后续 M30 / 前端对接 / PPT 展示也应保持这个约束。

---

## 4. 当前团队和展示状态

当前小组状态：

```text
用户本人负责后端。
前端同学还没有真正完成最终展示界面。
```

已有：

```text
M16 Textual reference frontend
M25 showcase demo
M29 final defense demo runner
final report draft
defense outline
final demo script
final claims checklist
final results summary
defense system overview figure
```

因此最终展示不要依赖复杂前端是否完成。后端已有 terminal demo 和 report assets 兜底。

如果前端同学开始做，建议只做轻量展示，不要让她重写后端逻辑。

前端建议展示组件：

```text
Task list
Event stream
FailureMemory card
EnvRepairPlan card
PatchPlan card
PatchSafetyReviewer card
Verification result card
Reproducibility manifest link
Memory retrieval result card
Claim boundary / benchmark scope note
```

前端不要做：

```text
重写 BackendController
直接调用内部 runner/tool
引入数据库
做复杂 web dashboard
依赖真实 API key
依赖 public benchmark 下载
让前端触发真实 LLM
让前端直接 apply patch 到外部 repo
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
not real LLM evaluation
not real-world generalization proof
```

不要说：

```text
SciCodePilot achieves SOTA.
SciCodePilot outperforms SWE-agent / AutoCodeRover / OpenHands.
SciCodePilot completed SWE-bench.
SciCodePilot completed BugsInPy.
SciCodePilot proves real-world generalization.
Mock LLM repair represents real LLM performance.
Memory retrieval proves LLM repair improvement.
External repo smoke test is public benchmark evaluation.
```

---

## 6. M27：FailureMemory Retrieval and Memory-Augmented Planning Pack

### 6.1 M27 目标

M27 的目标是：

```text
让 FailureMemory 从单次结构化记录升级为可检索的本地 memory。
```

M27 没有做真实 LLM，也没有改变 benchmark 默认路径。它只是：

```text
导出 memory records
存储到 JSONL
做 deterministic retrieval
构造未来 structured PatchPlan planner 的 memory-augmented prompt
```

### 6.2 M27 新增/修改文件

新增 memory store / retrieval：

```text
scicodepilot/memory/record.py
scicodepilot/memory/store.py
scicodepilot/memory/__init__.py
```

新增 prompt builder：

```text
scicodepilot/llm/memory_prompt_builder.py
```

小修 lazy import 避免循环导入：

```text
scicodepilot/llm/__init__.py
```

新增 scripts：

```text
scripts/export_failure_memory_records.py
scripts/run_memory_retrieval_demo.py
```

新增 docs / assets：

```text
docs/m27_memory_retrieval.md
report_assets/tables/memory_retrieval_examples.md
```

生成 memory JSONL：

```text
artifacts/failure_memory/memory_records.jsonl
```

新增 tests：

```text
tests/test_failure_memory_store.py
tests/test_failure_memory_retrieval.py
tests/test_memory_prompt_builder.py
tests/test_memory_retrieval_demo.py
tests/test_failure_memory_export.py
```

### 6.3 M27 验证结果

运行过：

```bash
python scripts/export_component_metrics.py --latest
cat report_assets/tables/component_metrics.md
python scripts/export_failure_memory_records.py --latest
python scripts/run_memory_retrieval_demo.py
pytest -q
```

关键结果：

```text
component metrics 保持修复后的行为：diagnosis pass count | 10/10
failure memory export 成功：record_count: 10
memory retrieval demo 输出目录：
/home/zengl/projects/SciCodePilot/outputs/memory_retrieval/20260604_101204
top retrieved memory:
internal_controlled_repair_tensor_shape_001
score:
2.028947
pytest -q:
170 passed in 48.33s
```

### 6.4 M27 当前限制

必须如实表述：

```text
retrieval 是 deterministic token matching，不是 embedding retrieval。
prompt builder 只构造未来 ICL prompt，不调用真实 LLM。
memory records 来自 internal controlled benchmark metadata/summary，不是 public benchmark evidence。
memory-augmented planning 没有变成默认 benchmark path。
```

---

## 7. M28：Memory Retrieval Evaluation and Report Integration Pack

### 7.1 M28 目标

M28 的目标是：

```text
把 M27 的 memory retrieval 从 demo 功能升级为可报告、可复现、可答辩的 component-level evaluation。
```

M28 不做真实 LLM，不做 public benchmark。它只评估：

```text
deterministic FailureMemory retrieval 是否能在 internal controlled records 上找回相关 memory。
```

### 7.2 M28 新增/修改文件

新增：

```text
scripts/evaluate_memory_retrieval.py
report_assets/tables/memory_retrieval_eval.md
tests/test_memory_retrieval_eval.py
```

生成 eval artifacts：

```text
/home/zengl/projects/SciCodePilot/outputs/memory_retrieval_eval/20260604_102125/summary.md
/home/zengl/projects/SciCodePilot/outputs/memory_retrieval_eval/20260604_102125/summary.json
```

修改：

```text
docs/final_report_draft.md
docs/table_and_figure_inventory.md
report_assets/tables/component_metrics.md
```

### 7.3 M28 验证命令

运行过：

```bash
python scripts/export_component_metrics.py --latest
cat report_assets/tables/component_metrics.md
python scripts/export_failure_memory_records.py --latest
python scripts/run_memory_retrieval_demo.py
python scripts/evaluate_memory_retrieval.py --latest
pytest -q
```

### 7.4 M28 关键指标

```text
record_count: 10
top_k: 3
total_queries: 10
top1_self_match_count: 10
top3_self_match_count: 10
top1_error_type_match_count: 10
top3_error_type_match_count: 10
source_repair_query_count: 8
env_or_data_query_count: 2
empty_result_count: 0
pytest -q: 174 passed in 49.13s
```

### 7.5 M28 解释边界

答辩时应该这样说：

```text
M28 是 memory retrieval component-level sanity evaluation。它验证 deterministic retrieval 在 internal controlled memory records 上可以稳定找回对应/同类记录。
```

不能这样说：

```text
M28 证明 LLM 修复性能提升。
M28 证明 memory retrieval 对真实 bug 有泛化。
M28 是 embedding retrieval benchmark。
M28 是 public benchmark result。
```

当前 memory data 每个 error type 大多只有一条记录，所以：

```text
exact self retrieval 是可复现性检查。
same-error retrieval beyond identical record 受数据规模限制。
```

---

## 8. M29：Final Report and Defense Integration Pack

### 8.1 M29 目标

M29 的目标是：

```text
停止继续堆算法功能，把现有系统收口成最终报告、demo 和答辩材料。
```

M29 不新增核心算法，不接真实 LLM，不接 public benchmark。

### 8.2 M29 新增文件

新增：

```text
docs/defense_outline.md
docs/final_demo_script.md
docs/final_claims_checklist.md
report_assets/tables/final_results_summary.md
report_assets/figures/defense_system_overview.md
scripts/run_final_defense_demo.py
tests/test_final_defense_assets.py
```

最新生成 eval artifacts：

```text
/home/zengl/projects/SciCodePilot/outputs/memory_retrieval_eval/20260604_103806/summary.md
/home/zengl/projects/SciCodePilot/outputs/memory_retrieval_eval/20260604_103806/summary.json
```

### 8.3 M29 修改文件

修改：

```text
docs/final_report_draft.md
docs/table_and_figure_inventory.md
report_assets/tables/component_metrics.md
report_assets/tables/memory_retrieval_eval.md
```

### 8.4 M29 验证命令

运行过：

```bash
python scripts/run_final_defense_demo.py --help
python scripts/run_final_defense_demo.py
python scripts/export_component_metrics.py --latest
python scripts/evaluate_memory_retrieval.py --latest
pytest -q
```

### 8.5 M29 验证结果

```text
Final defense demo ran offline.
Boundary lines printed:
public_benchmark_executed: false
real_llm_called: false
external_baseline_comparison: false

pytest -q:
181 passed in 48.23s
```

确认：

```text
BackendController public API was not changed.
No real LLM calls were added.
No new dependencies were installed.
No public benchmark was downloaded or run.
No SOTA or external baseline claim was introduced.
```

---

## 9. 当前最终结果表

`report_assets/tables/final_results_summary.md` 当前关键内容：

| Metric | Value |
|---|---|
| Controlled tasks | 10 |
| Diagnosis pass count | 10/10 |
| Source-code repair tasks | 8 |
| Env/data routing tasks | 2 |
| Patch plan count | 8 |
| Env repair plan count | 2 |
| Patch review count | 8 |
| Patch applied count | 8 |
| Verification success count | 8 |
| Scored task count | 8 |
| Average score | 1.0 |
| Safety stress case pass count | 10 |
| Failure memory record count | 10 |
| Memory retrieval total queries | 10 |
| Memory retrieval top-1 self match | 10/10 |
| Memory retrieval top-3 self match | 10/10 |
| Memory retrieval top-1 error-type match | 10/10 |
| Memory retrieval top-3 error-type match | 10/10 |
| External repo smoke interface | Implemented |
| Public benchmark evaluation | Not executed |
| Real LLM evaluation | Not executed |

必须附带说明：

```text
These results are scoped to internal controlled benchmark and component-level evaluation. They do not claim public benchmark performance, SOTA comparison, or real-world generalization.
```

---

## 10. 当前答辩主线

答辩建议主线：

```text
第一层：科研 Python/ML 代码失败复杂，不能所有错误都用直接代码 patch 解决。
第二层：SciCodePilot 把失败转成结构化 FailureMemory，显式区分 source-code / env / data failure。
第三层：source-code failure 进入 PatchPlanner 和 PatchSafetyReviewer；env/data failure 进入 EnvRepairPlan。
第四层：所有 patch 只在 isolated workspace 中应用和验证，原始 benchmark 不被污染。
第五层：系统输出 events、summary、score、manifest、tables，保证可审计和可复现。
第六层：M27/M28 把 FailureMemory 进一步变成本地 JSONL memory，可以 deterministic retrieval，并为未来 memory-augmented structured planner 构造 prompt。
第七层：当前结果是 internal controlled benchmark 和 component-level evaluation，不是 public benchmark 或 SOTA。
```

答辩最核心一句话：

```text
SciCodePilot 不是直接让 LLM 根据 traceback 改代码，而是把失败转成结构化 FailureMemory，先区分源码、环境和数据问题，再经过安全审查、隔离验证和复现记录，形成一个可审计、可复现的科研代码修复 agent pipeline。
```

---

## 11. 当前 final report 状态

`docs/final_report_draft.md` 已经包含：

```text
Abstract
Introduction
Related Work
Benchmark and Task Design
Method
Experiments
Internal Controlled Benchmark Setup
Main Results
Internal Controlled Ablation
Safety Stress Cases
Reproducibility Bundle
External Repo Smoke Interface
Memory Retrieval Evaluation
Public Benchmark Extension Plan
Limitations
Conclusion
```

报告当前关键边界正确：

```text
internal 10-task controlled benchmark
not public benchmark
not SOTA comparison
not real LLM performance
not real-world generalization
```

报告当前结论方向：

```text
The final packaged result is a defense-ready backend system with controlled benchmark results, safety and reproducibility assets, an external repo smoke interface, and deterministic FailureMemory retrieval evaluation.
```

后续如果继续改 final report，主要做：

```text
语言润色
图表 caption
把 final_results_summary 融入正文
把 defense_system_overview 转成 PPT 图
统一术语
避免 claim 过度
```

不要新增未经验证的实验 claim。

---

## 12. 当前 table / figure inventory 状态

`docs/table_and_figure_inventory.md` 已经登记：

Tables：

```text
report_assets/tables/ablation_table.md
report_assets/tables/safety_table.md
report_assets/tables/repro_bundle_manifest.md
report_assets/tables/component_metrics.md
report_assets/tables/memory_retrieval_examples.md
report_assets/tables/memory_retrieval_eval.md
report_assets/tables/final_results_summary.md
```

Figures：

```text
report_assets/figures/event_flow.md
report_assets/figures/system_pipeline.md
report_assets/figures/defense_system_overview.md
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
docs/m27_memory_retrieval.md
docs/public_benchmark_plan.md
docs/public_benchmark_adapter.md
docs/defense_outline.md
docs/final_demo_script.md
docs/final_claims_checklist.md
scripts/run_final_defense_demo.py
```

当前 inventory 认为这些资产 ready，但表格 caption、Mermaid visual styling 和 PPT 化还可以人工润色。

---

## 13. 当前 final demo 流程

`docs/final_demo_script.md` 建议答辩 terminal demo 顺序：

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev

python scripts/run_showcase_demo.py

python scripts/export_component_metrics.py --latest
cat report_assets/tables/component_metrics.md

python scripts/run_external_repo_smoke.py --help

python scripts/export_failure_memory_records.py --latest
python scripts/run_memory_retrieval_demo.py
python scripts/evaluate_memory_retrieval.py --latest

pytest -q
```

每一步对应解释：

```text
run_showcase_demo.py：
展示 diagnosis、FailureMemory、patch proposal、PatchReview、verification、EnvRepairPlan、safety stress summaries。

export_component_metrics.py：
展示 internal controlled benchmark metrics。

run_external_repo_smoke.py --help：
展示外部本地 repo smoke 入口，不修改原 repo。

export_failure_memory_records.py：
展示 internal cases 可以导出为 JSONL memory。

run_memory_retrieval_demo.py：
展示 deterministic top-k retrieval 和 memory-augmented prompt construction。

evaluate_memory_retrieval.py：
展示 retrieval sanity metrics。

pytest -q：
展示全项目离线 deterministic tests 通过。
```

如果答辩时间短，可以不现场跑 `pytest -q`，只展示最近测试结果和 demo runner 输出。

---

## 14. 老师可能追问与推荐回答

### Q1：你和直接让 ChatGPT 修代码有什么区别？

推荐回答：

```text
直接让 ChatGPT 修代码通常是 free-form patch。SciCodePilot 把失败先转成结构化 FailureMemory，再区分源码、环境和数据问题，source-code failure 才进入 PatchPlanner，env/data failure 进入 EnvRepairPlan。所有 patch 还要经过 PatchSafetyReviewer，并只在 isolated workspace 中应用和验证。因此它强调的是可审计、安全边界和复现，而不是一次性生成答案。
```

### Q2：FailureMemory 到底是什么？

推荐回答：

```text
FailureMemory 是一次失败的结构化记录，包括 error type、evidence、root-cause hypothesis、repair action 等。M27 之后它还可以被导出为 JSONL memory records，用 deterministic retrieval 找回相似失败，为未来 structured PatchPlan prompt 提供上下文。
```

### Q3：为什么只有 10 个 benchmark？

推荐回答：

```text
当前 10 个 task 是 internal controlled benchmark，目的是验证 pipeline 的每个组件：diagnosis、routing、patch planning、safety review、isolated verification、reproducibility 和 memory retrieval。它不是 public benchmark。下一步应该是小规模 public benchmark pilot，而不是把当前结果夸大成泛化性能。
```

### Q4：跑 BugsInPy / SWE-bench 了吗？

推荐回答：

```text
没有。当前只做了 public benchmark adapter skeleton 和 public benchmark plan，没有下载或运行 BugsInPy / SWE-bench，也不报告 public benchmark performance。
```

### Q5：memory retrieval 是不是只是字符串匹配？

推荐回答：

```text
是。当前是 deterministic token matching，加上 error_type、exception_type 和 path-like terms 的 bonus。这样做是为了离线可复现和 component-level sanity evaluation。embedding retrieval 和真实 LLM evaluation 是未来工作。
```

### Q6：用了真实 LLM 吗？

推荐回答：

```text
当前 evaluation 不依赖真实 LLM。已有 mock LLM path 和 memory-augmented prompt builder，用于验证 structured planner 可以接入同一安全 pipeline，但不代表 real LLM repair performance。
```

### Q7：为什么不自动 pip install？

推荐回答：

```text
自动安装会改变实验环境，破坏复现性，也可能带来安全风险。SciCodePilot 对 missing_module 生成 EnvRepairPlan，让人决定如何修改环境，而不是自动安装。
```

### Q8：为什么不创建 missing file？

推荐回答：

```text
创建假数据会掩盖真实的数据可用性和复现问题。missing_file 被识别为数据/配置问题，并生成 EnvRepairPlan，而不是伪造文件让测试通过。
```

### Q9：PatchSafetyReviewer 保护什么？

推荐回答：

```text
它检查 predefined unsafe patterns，比如 path traversal、绝对路径、修改 benchmark/tests/outputs、依赖安装、shell 命令、rm -rf、sudo、eval/exec、subprocess/os.system 等。它不是完整 sandbox security，但能阻断当前定义的高风险 patch pattern。
```

### Q10：External repo smoke test 证明了什么？

推荐回答：

```text
它证明系统入口不局限于内置 benchmark task runner，可以对任意本地 Python repo 复制到 isolated workspace 后运行命令，并生成 diagnosis 或 non-applying repair-plan summary。但它不是 public benchmark，不比较外部 baseline，也不修改原始 repo。
```

---

## 15. 当前 safe claims / prohibited claims

### Safe Claims

可以说：

```text
SciCodePilot evaluates an internal controlled benchmark.
SciCodePilot reports component-level evaluation assets.
SciCodePilot uses structured FailureMemory.
SciCodePilot separates diagnosis from repair.
SciCodePilot routes source-code failures separately from env/data failures.
SciCodePilot uses safety-constrained patch planning.
SciCodePilot verifies approved internal benchmark repairs in isolated workspaces.
SciCodePilot exports a reproducibility manifest.
SciCodePilot includes an external repo smoke interface.
SciCodePilot includes deterministic memory retrieval evaluation.
```

### Claims That Need Qualification

必须加限定：

```text
"The system solves the benchmark" → internal 10-task controlled benchmark.
"The memory retrieval works" → deterministic token matching over internal controlled records.
"The LLM planner path exists" → mock/prompt-building behavior unless real LLM evaluation is added later.
"The external repo interface works" → smoke diagnosis/planning only, copied workspace only.
"Safety reviewer blocks unsafe patches" → predefined unsafe patterns, not complete sandbox security.
```

### Prohibited Claims

不能说：

```text
SOTA.
Outperforms SWE-agent / AutoCodeRover / OpenHands / other agents.
Completed SWE-bench.
Completed BugsInPy.
Public benchmark performance.
Real-world generalization.
Real LLM repair performance.
Fully secure sandbox.
Automatic environment repair.
Automatic dataset repair.
```

---

## 16. 当前建议提交状态

M27、M28、M29 做完后应该分别提交。若还没有提交 M29，建议：

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev

git status

git add docs/defense_outline.md \
        docs/final_demo_script.md \
        docs/final_claims_checklist.md \
        report_assets/tables/final_results_summary.md \
        report_assets/figures/defense_system_overview.md \
        scripts/run_final_defense_demo.py \
        tests/test_final_defense_assets.py \
        docs/final_report_draft.md \
        docs/table_and_figure_inventory.md \
        report_assets/tables/component_metrics.md \
        report_assets/tables/memory_retrieval_eval.md

git commit -m "Add final defense integration assets"
```

如果项目习惯提交 generated evidence，可额外提交：

```bash
git add outputs/memory_retrieval_eval/20260604_103806/summary.md \
        outputs/memory_retrieval_eval/20260604_103806/summary.json
```

如果项目一般不提交 `outputs/`，则不要提交它们，只保留 `report_assets/tables/memory_retrieval_eval.md`。

提交后最终验证：

```bash
git status
python scripts/run_final_defense_demo.py
pytest -q
```

---

## 17. 后续最推荐方向

### 17.1 最高优先级：PPT 和答辩材料

现在最该做的是：

```text
PPT
答辩讲稿
demo 截图
终端 demo 预演
前端对接说明
最终报告润色
```

不要继续加功能。

建议 PPT 结构：

```text
1. Title: SciCodePilot
2. Problem: scientific Python/ML code failures are not only source-code bugs
3. Key idea: structured failure-memory agent, not direct LLM patching
4. System overview
5. FailureMemory + source/env/data routing
6. PatchSafetyReviewer + isolated verification
7. Internal controlled benchmark
8. Final results summary
9. FailureMemory retrieval: M27/M28
10. External repo smoke interface
11. Limitations
12. Future work / conclusion
```

### 17.2 前端同学对接

给前端同学的最小 contract：

```text
只调用 BackendController public API：
list_tasks()
get_task(task_id)
run_task(task_id, mode, confirm_apply=False)

只使用 event_to_dict / event_to_json 序列化事件。
不要直接调用内部 runner/tool/planner/applier。
不要引入真实 LLM。
不要触发 public benchmark。
不要让前端直接写外部 repo。
```

前端展示优先级：

```text
1. Task list
2. Run diagnosis / repair
3. Event stream timeline
4. FailureMemory card
5. EnvRepairPlan card
6. PatchPlan card
7. PatchSafetyReviewer result
8. Verification result
9. Reproducibility/report assets links
10. Memory retrieval demo card（可选）
```

### 17.3 可选 M30

只有在 PPT、报告、demo、前端对接都完成后，才考虑 M30。

最稳的 M30 候选：

```text
M30A: Frontend Integration Contract Pack
```

内容：

```text
docs/frontend_integration_contract.md
docs/frontend_event_examples.md
report_assets/mockups/failure_memory_card.md
report_assets/mockups/patch_review_card.md
report_assets/mockups/env_repair_plan_card.md
tests/test_frontend_contract_docs.py
```

不建议优先做：

```text
M30 Real LLM Structured Planner Smoke Test
```

因为它会引入 API key、网络、费用、输出不稳定和 claim 风险。除非老师明确要求“必须展示真实 LLM”，否则不要做。

如果一定要做真实 LLM，只能作为 optional appendix：

```text
M30 Optional Real LLM Structured Planner Smoke Test
```

并保持：

```text
只跑 2–3 个 internal tasks
LLM 只输出 structured PatchPlan JSON
不直接改文件
不执行 shell
不安装依赖
patch 仍过 PatchSafetyReviewer
记录 invalid JSON / latency / token / safety review result
不作为主结果
不声称 real-world/general public benchmark performance
```

---

## 18. 后续不要做什么

当前不要做：

```text
大规模 SWE-bench / BugsInPy
OpenHands / SWE-agent / AutoCodeRover baseline comparison
LangGraph / LangChain 重构
FAISS / embedding / vector DB
真实 LLM 默认路径
LoRA / 小模型训练
继续堆 20/30 个 toy benchmark tasks
复杂 web dashboard
修改 BackendController public API
自动 pip install / conda install
自动创建 missing file / fake data
绕过 PatchSafetyReviewer
把 external repo smoke 写成 benchmark result
把 memory retrieval 写成 LLM 性能提升
```

当前最大风险不是功能不够，而是：

```text
claim 过度
PPT 主线不清楚
demo 太长
前端不稳定
老师误解为 public benchmark / SOTA claim
```

---

## 19. 新 GPT 接手后的第一步

新 GPT / Codex 接手后，第一步不要设计新功能。先做：

```bash
cd /home/zengl/projects/SciCodePilot
source /home/zengl/miniconda3/etc/profile.d/conda.sh
conda activate scicodepilot-dev
git status
pytest -q
python scripts/run_final_defense_demo.py
```

然后检查：

```bash
cat report_assets/tables/final_results_summary.md
cat docs/final_claims_checklist.md
cat docs/final_demo_script.md
```

如果用户问“接下来怎么做”，默认回答应是：

```text
先准备 PPT / 答辩稿 / demo 截图 / 前端对接材料，不继续加核心功能。
```

如果用户问“M30 做什么”，默认建议应是：

```text
M30A: Frontend Integration Contract Pack
```

而不是直接做真实 LLM 或 public benchmark。

---

## 20. 新 GPT 可以这样开场

```text
我已经阅读 SciCodePilot M27–M29 交接文档。当前系统已经完成 FailureMemory retrieval、memory retrieval evaluation 和 final defense integration。最新测试状态为 pytest 181 passed。当前项目应进入答辩材料和前端对接收口阶段，而不是继续堆功能。后续必须保持 BackendController public API 不变，不接真实 LLM，不下载 public benchmark，不声称 SOTA。最推荐下一步是准备 PPT、答辩讲稿、demo 截图，或做 M30A: Frontend Integration Contract Pack。
```

---

## 21. 最重要提醒

当前项目可以这样理解：

```text
不是“只有 10 个 toy bug 的修复脚本”，
而是一个围绕科研代码修复构建的可审计 agent backend：
它把失败结构化为 FailureMemory，
显式区分源码/环境/数据问题，
通过安全审查和隔离验证控制 patch 风险，
通过 manifest 和 report assets 记录复现证据，
通过 memory retrieval 展示 agent memory 的可扩展方向。
```

但当前证据只能支持：

```text
internal controlled benchmark
component-level evaluation
defense-ready backend system
```

不能支持：

```text
public benchmark performance
real-world generalization
SOTA comparison
real LLM repair performance
```

后续所有报告、PPT、前端展示、M30 设计都必须守住这个边界。
