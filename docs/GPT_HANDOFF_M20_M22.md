SciCodePilot GPT 设计交接文档：M20–M22
0. 项目基本信息

项目名：SciCodePilot

项目路径：

/home/zengl/projects/SciCodePilot

运行环境：

WSL Ubuntu
Conda 环境：scicodepilot-dev

进入项目标准命令：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev

长期约束：

所有命令必须在 WSL Ubuntu 中运行。
不要在 Windows PowerShell 中运行项目命令。
涉及 Python / pip 时，优先使用当前 conda 环境中的 python / pip。
1. 当前项目定位

SciCodePilot 当前应被定义为：

A structured failure-memory agent for reliable scientific code repair and reproducibility.

中文定位：

面向可靠科研代码修复与复现的结构化失败记忆 Agent 系统。

它不是一个普通代码聊天机器人，也不是简单 API wrapper，而是一个事件流驱动的科研代码 diagnosis / repair benchmark 系统。

当前核心链路：

benchmark task
→ run command
→ capture stdout/stderr
→ parse error
→ build structured FailureMemory
→ choose source-code repair or env/data repair
→ propose PatchPlan or EnvRepairPlan
→ PatchSafetyReviewer
→ optional confirmation
→ isolated workspace apply
→ verification
→ hidden evaluator
→ score.json
→ experiment summary / frontend event stream

当前研究主线已经明确：

Structured failure memory, environment issue routing, and patch safety review 是否能提升科研代码修复 Agent 的可靠性、可解释性和安全性？

这已经写入 docs/research_questions.md，其中 H1–H4 分别对应 FailureMemory、EnvDoctor、PatchSafetyReviewer、workspace isolation。

2. 必须保持的 public API

当前前端和外部调用只应依赖：

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json

BackendController public API 不要改：

list_tasks()
get_task(task_id)
run_task(task_id, mode, confirm_apply=False)

mode 只能是：

diagnosis
repair

不要改成：

diagnose

前端同学、文档网站、Textual reference frontend 都应围绕这个接口，不要直接调用内部 runner、tool、PatchPlanner、PatchApplier、EnvDoctor 或 suite runner。

3. 当前 milestone 总览

截至 M22，项目完成状态如下：

Milestone	状态
M13	benchmark 扩展到 6 个任务
M14	workspace isolation / hidden evaluator / score.json
M15	EnvDoctor，missing_module / missing_file 不做源码 patch
M16	Textual reference frontend
M17	optional LLM PatchPlanner adapter，默认关闭
M18	multi-provider LLM planner：mock / deepseek / gemini / openai / disabled
M19	Patch Safety Reviewer
M20	Research Evaluation Pack
M21	Benchmark Expansion：6 tasks → 10 tasks
M22	Ablation Experiments and Result Analysis
4. M20：Research Evaluation Pack
4.1 M20 设计动机

M20 不是继续增加复杂 Agent 功能，而是把项目从“后端 demo”转成“可写最终报告的研究型系统”。

M20 的核心目标：

明确研究问题
明确实验协议
明确失败类型 taxonomy
明确 safety cases
生成可复现实验结果
生成可引用结果表
4.2 M20 新增文件

M20 完成后新增：

scripts/run_experiments.py
scripts/export_results_table.py
docs/research_questions.md
docs/experiment_protocol.md
docs/failure_taxonomy.md
docs/safety_cases.md
tests/test_research_docs.py
tests/test_experiment_scripts.py
4.3 M20 修改文件

M20 修改：

tests/test_patch_safety_reviewer.py

补充了更多 safety cases，包括：

benchmark/
tests/
.git/
requirements.txt
pyproject.toml
conda install
sudo
subprocess
eval
exec
4.4 M20 实验脚本

quick experiments：

python scripts/run_experiments.py --quick

导出最新结果表：

python scripts/export_results_table.py --latest

M20 生成过：

outputs/experiments/20260522_183104/summary.json
outputs/experiments/20260522_183104/results_table.md

summary.json 记录：

command
return_code
stdout_tail
stderr_tail
parsed_summary
4.5 M20 文档内容

research_questions.md：

研究问题
H1-H4 假设
项目贡献

experiment_protocol.md：

benchmark task table
metrics
experimental settings
hidden evaluator limitation
contamination check

failure_taxonomy.md：

error types
evidence source
handling modules
boundaries
possible failure modes

docs/safety_cases.md：

PatchSafetyReviewer 应拦截的危险 patch cases
4.6 M20 验收状态

M20 完成时：

pytest -q: 117 passed
run_experiments.py --quick: 成功
export_results_table.py --latest: 成功

当时 benchmark 仍为 6 tasks：

diagnosis suite:
total_tasks=6
diagnosis_pass_count=6

repair without apply:
patch_applied_count=0
env_repair_plan_count=2

repair --confirm-apply:
patch_review_count=4
patch_review_blocked_count=0
patch_applied_count=4
verification_success_count=4
scored_task_count=4
env_repair_plan_count=2
average_score=1.0

mock LLM repair:
average_score=1.0
5. M21：Benchmark Expansion
5.1 M21 设计动机

M21 的目标是把 benchmark 从 6 个任务扩展到 10 个任务，使它更像科研代码复现 benchmark，而不是少量 toy demo。

M21 不改变 BackendController public API。

5.2 M21 新增 4 个 task

新增任务：

repair_device_mismatch_007
repair_loss_input_008
repair_collate_fn_009
repair_config_key_010

当前 benchmark 共 10 个 task：

Task	Error Type	Category
repair_tensor_shape_001	tensor_shape	source-code repair
repair_dtype_mismatch_002	dtype_mismatch	source-code repair
repair_missing_module_003	missing_module	env/data diagnosis
repair_missing_file_004	missing_file	env/data diagnosis
repair_entrypoint_error_005	entrypoint_error	source-code repair
repair_label_shape_006	label_shape	source-code repair
repair_device_mismatch_007	device_mismatch	source-code repair
repair_loss_input_008	loss_input_error	source-code repair
repair_collate_fn_009	collate_fn_error	source-code repair
repair_config_key_010	config_key_error	source-code repair

M20 的 experiment_protocol.md 原本列出 6-task benchmark；M21 后已经更新为 10-task benchmark。实验协议中的指标包括 diagnosis、patch plan、patch review、env repair plan、verification、score 等。

5.3 新增任务修复逻辑
repair_device_mismatch_007

错误类型：

device_mismatch

修复逻辑：

input_device = "cuda:0"
改为：
input_device = "cpu"

目标：

统一 device，避免 CPU-only 环境不稳定。
repair_loss_input_008

错误类型：

loss_input_error

修复逻辑：

target_kind = "probabilities"
改为：
target_kind = "class_indices"

目标：

修复 loss 输入格式错误。
repair_collate_fn_009

错误类型：

collate_fn_error

修复逻辑：

return {"features": xs, "labels": ys}

改为：

return {"x": xs, "y": ys}

因为训练循环期望 batch dictionary 中包含 x 和 y。上传的 task 文件也明确说明：training loop expects a batch dictionary with x and y，但 collate function 返回了 mismatched structure。

repair_config_key_010

错误类型：

config_key_error

修复逻辑：

config["learningrate"]

改为：

config["learning_rate"]
5.4 M21 修改文件

M21 修改：

scicodepilot/tools/traceback_parser.py
scicodepilot/memory/failure_memory.py
scicodepilot/repair/patch_planner.py
scicodepilot/review/patch_safety_reviewer.py
tests/test_benchmark_tasks.py
tests/test_traceback_parser.py
tests/test_failure_memory.py
tests/test_patch_planner.py
tests/test_suite_runner.py
docs/experiment_protocol.md
docs/failure_taxonomy.md
docs/final_status.md
docs/architecture.md
scripts/run_showcase.py
5.5 M21 验收状态

M21 完成时：

pytest -q: 131 passed

diagnosis suite：

total_tasks=10
diagnosis_pass_count=10

repair without apply：

patch_plan_count=8
patch_applied_count=0
env_repair_plan_count=2

repair --confirm-apply：

patch_plan_count=8
patch_review_count=8
patch_review_blocked_count=0
patch_applied_count=8
verification_success_count=8
scored_task_count=8
env_repair_plan_count=2
average_score=1.0

mock LLM repair：

patch_review_count=8
patch_review_blocked_count=0
average_score=1.0

Experiment output：

summary: /home/zengl/projects/SciCodePilot/outputs/experiments/20260522_194640/summary.json
table:   /home/zengl/projects/SciCodePilot/outputs/experiments/20260522_194640/results_table.md
5.6 M21 原始 benchmark 污染检查

已确认原始 bug 仍保留：

classifier_expected_dim = 128
dtype=torch.float64
mainn()
batch_size + 1
input_device = "cuda:0"
target_kind = "probabilities"
return {"features": xs, "labels": ys}
config["learningrate"]

这意味着 workspace isolation 仍有效，repair/apply 不污染 benchmark/tasks/*/repo。

6. M22：Ablation Experiments and Result Analysis
6.1 M22 设计动机

M22 的目标是把当前系统整理成最终报告可用的：

量化实验
消融实验
安全分析
结果表格
实验分析文档

M22 不新增核心 Agent 功能，不改变 BackendController public API。

6.2 M22 新增文件

M22 新增：

scripts/run_ablation_experiments.py
scripts/export_ablation_tables.py
docs/ablation_study.md
docs/results_analysis.md
tests/test_ablation_scripts.py
6.3 M22 修改文件

M22 修改：

docs/final_status.md
docs/experiment_protocol.md
6.4 M22 生成结果

M22 生成：

outputs/ablations/20260522_195640/ablation_summary.json
outputs/ablations/20260522_195640/ablation_table.md
outputs/ablations/20260522_195640/safety_table.md
report_assets/tables/ablation_table.md
report_assets/tables/safety_table.md

其中 report_assets/tables/*.md 可以直接放进最终报告的 Experiments / Results 章节。

6.5 M22 实验组

M22 包含以下实验：

diagnosis_only
repair_without_apply
full_rule_based_repair
mock_llm_repair
safety_stress_cases

每组含义：

Variant	Purpose
diagnosis_only	只验证错误识别能力，不修复
repair_without_apply	验证 patch planning、env routing、safety review，但不修改代码
full_rule_based_repair	当前主系统，deterministic rule-based PatchPlanner
mock_llm_repair	验证 LLM planner 路径也经过 safety gate
safety_stress_cases	验证 PatchSafetyReviewer 对危险 patch 的拦截能力
6.6 M22 量化结果

M22 验收结果：

pytest -q: 136 passed
python scripts/run_ablation_experiments.py --quick --include-safety: 成功
python scripts/export_ablation_tables.py --latest: 成功

各实验结果：

diagnosis_only
total_tasks=10
diagnosis_pass_count=10
repair_without_apply
patch_plan_count=8
patch_review_count=8
patch_applied_count=0
env_repair_plan_count=2
full_rule_based_repair
patch_applied_count=8
verification_success_count=8
scored_task_count=8
average_score=1.0
mock_llm_repair
patch_review_count=8
patch_review_blocked_count=0
average_score=1.0
safety_stress_cases
10 passed
6.7 M22 suite 复验

diagnosis suite：

total_tasks=10
diagnosis_pass_count=10

repair without apply：

patch_plan_count=8
patch_applied_count=0
env_repair_plan_count=2

repair with confirm apply：

patch_review_count=8
patch_review_blocked_count=0
patch_applied_count=8
verification_success_count=8
scored_task_count=8
average_score=1.0

mock LLM repair：

patch_review_count=8
patch_review_blocked_count=0
average_score=1.0
6.8 M22 原始 benchmark 污染检查

已确认原始 bug 仍保留：

classifier_expected_dim = 128
dtype=torch.float64
mainn()
batch_size + 1
input_device = "cuda:0"
target_kind = "probabilities"
return {"features": xs, "labels": ys}
config["learningrate"]

BackendController public API 未修改。

7. 当前最重要的技术贡献

新 GPT 接手后，应把以下 5 点作为最终报告核心贡献，不要再把项目讲成普通 demo。

7.1 Event-driven scientific code repair backend

项目通过事件流组织整个 Agent workflow：

TaskStarted
CommandStarted
CommandOutput
ErrorDetected
FailureMemoryCreated
EnvRepairPlanCreated
PatchProposed
PatchReviewCreated
PatchApprovalRequired
PatchApplied
VerificationFinished
TaskFinished

前端、showcase、实验脚本都可以基于事件流解释系统行为。

7.2 Structured FailureMemory

结构化失败记忆将原始 stderr / traceback 转成：

error_type
evidence
root cause hypothesis
repair action

它比自由文本 reflection 更适合：

解释
消融
统计
前端卡片展示
错误类型分析

当前 failure_taxonomy.md 已经整理了支持的 error types、evidence source、handling modules 和 boundary。

7.3 Source-code repair vs env/data repair routing

系统不会把 missing_module / missing_file 强行当作源码 bug。

missing_module → EnvRepairPlanCreated
missing_file   → EnvRepairPlanCreated

不自动：

pip install
conda install
创建假数据文件
吞掉异常
删除 import

这是科研复现可靠性的重要边界。

7.4 PatchSafetyReviewer

所有 PatchPlan 都必须经过：

PatchReviewCreated

安全 reviewer 会拦截：

absolute path
../ path traversal
benchmark path modification
outputs path modification
tests path modification
requirements.txt
pyproject.toml
pip install
conda install
rm -rf
sudo
os.system
subprocess
eval
exec
multi-file unsafe diff

M22 safety stress cases 已经通过：

10 passed
7.5 Workspace isolation + score.json evaluation

repair/apply 只能在：

outputs/workspaces/<run_id>/<task_id>/repo

中发生，不能污染：

benchmark/tasks/*/repo

hidden evaluator 当前是轻量版本，主要基于 entry command behavior 和 score.json。不要在报告中夸大成完整大型 hidden test suite。

8. 当前最终报告可引用材料
8.1 可直接引用文档
docs/research_questions.md
docs/experiment_protocol.md
docs/failure_taxonomy.md
docs/safety_cases.md
docs/ablation_study.md
docs/results_analysis.md
docs/final_status.md
docs/architecture.md

用途：

文件	用途
research_questions.md	Introduction / Research Questions
experiment_protocol.md	Experiment Setup
failure_taxonomy.md	Method / Benchmark / Error Analysis
safety_cases.md	Safety Analysis
ablation_study.md	Ablation Study
results_analysis.md	Results and Discussion
final_status.md	Project Completion / Appendix
architecture.md	Method / System Design
8.2 可直接引用表格
report_assets/tables/ablation_table.md
report_assets/tables/safety_table.md

用途：

Experiments section
Results section
PPT result slide
9. 当前验收命令清单

进入项目：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev

完整测试：

pytest -q

当前期望：

136 passed

diagnosis suite：

python scripts/run_benchmark_suite.py --mode diagnosis

期望：

total_tasks=10
diagnosis_pass_count=10

repair without apply：

python scripts/run_benchmark_suite.py --mode repair

期望：

patch_plan_count=8
patch_review_count=8
patch_applied_count=0
env_repair_plan_count=2

repair with confirm apply：

python scripts/run_benchmark_suite.py --mode repair --confirm-apply

期望：

patch_review_count=8
patch_review_blocked_count=0
patch_applied_count=8
verification_success_count=8
scored_task_count=8
env_repair_plan_count=2
average_score=1.0

mock LLM repair：

SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner

期望：

patch_review_count=8
patch_review_blocked_count=0
average_score=1.0

M20 experiment pack：

python scripts/run_experiments.py --quick
python scripts/export_results_table.py --latest

M22 ablation pack：

python scripts/run_ablation_experiments.py --quick --include-safety
python scripts/export_ablation_tables.py --latest

原始 benchmark 污染检查：

grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py
grep 'input_device = "cuda:0"' benchmark/tasks/repair_device_mismatch_007/repo/train.py
grep 'target_kind = "probabilities"' benchmark/tasks/repair_loss_input_008/repo/train.py
grep 'return {"features": xs, "labels": ys}' benchmark/tasks/repair_collate_fn_009/repo/train.py
grep 'config\["learningrate"\]' benchmark/tasks/repair_config_key_010/repo/train.py
10. 当前不要再做什么

新 GPT 接手时，不要继续盲目设计新功能。

尤其不要：

接 OpenHands
接 LangGraph
继续增加 LLM provider
改 BackendController public API
把 LLM planner 变成默认路径
让 EnvDoctor 自动 pip install
让 EnvDoctor 自动创建 missing file
让 patch 修改 benchmark 原始 repo
绕过 PatchSafetyReviewer
把 mode 改成 diagnose
夸大 hidden evaluator
继续无限扩 benchmark

当前系统功能已经够了。后面重点应该是：

报告
图表
slides
demo story
文档网站
前端展示
失败分析
贡献包装
11. M23 建议方向：Final Report Assets

新 GPT 继续时，建议 M23 不要再做核心后端，而是做：

M23：Final Report Assets

目标：

把 M20-M22 的研究问题、benchmark、实验、消融、安全分析整理成最终报告和 PPT 可用素材。

M23 应该优先产出：

report_assets/figures/system_pipeline.png 或 .md/.svg
report_assets/figures/event_flow.png 或 .md/.svg
report_assets/figures/benchmark_distribution.png
report_assets/tables/main_results.md
report_assets/tables/ablation_table.md
report_assets/tables/safety_table.md
docs/report_outline.md
docs/method_draft.md
docs/experiments_draft.md
docs/limitations_draft.md
docs/demo_script.md

M23 重点不是新增实验，而是把已有实验讲清楚。

12. M23 报告主线建议

最终报告推荐题目：

SciCodePilot: A Structured Failure-Memory Agent for Reliable Scientific Code Repair and Reproducibility

报告结构建议：

1. Abstract
2. Introduction
3. Related Work
4. Benchmark and Task Design
5. Method
   5.1 Event-driven Agent Pipeline
   5.2 Structured Failure Memory
   5.3 EnvDoctor for Environment/Data Failures
   5.4 Patch Planning and Safety Review
   5.5 Workspace Isolation and Evaluation
6. Experiments
   6.1 Benchmark Setup
   6.2 Main Results
   6.3 Ablation Study
   6.4 Safety Stress Cases
   6.5 Failure Analysis
7. Demo System
8. Limitations and Ethics
9. Conclusion
13. M23 需要强调的实验叙事

当前实验要这样讲：

不要说
我们在 10 个小任务上准确率 100%。
应该说
We construct a controlled 10-task benchmark covering common scientific code failures.
SciCodePilot successfully diagnoses all 10 tasks, repairs all 8 source-code repair tasks after confirmation, and routes 2 environment/data failures to EnvRepairPlan without unsafe automatic modification.

中文：

我们构建了一个受控的 10-task benchmark，覆盖科研代码复现中常见的 tensor shape、dtype、device、loss input、collate function、config key、missing module、missing file 等失败类型。SciCodePilot 能诊断全部 10 个任务，确认后修复全部 8 个源码错误，并将 2 个环境/数据问题正确路由为 EnvRepairPlan，而不是危险地自动改代码或伪造环境。
14. M23 需要强调的限制

报告里必须主动承认限制，这会显得科研 taste 更好：

1. Benchmark 规模仍小，当前只有 10 个 controlled tasks。
2. Hidden evaluator 当前较轻量，主要检查 entry command 和 score.json。
3. Rule-based PatchPlanner 对当前错误模式有效，但尚未覆盖真实大型科研仓库。
4. LLM planner 虽已接入 multi-provider，但默认关闭，真实 provider 尚未系统评测。
5. EnvDoctor 只生成 repair plan，不自动安装依赖或下载数据。
6. SafetyReviewer 是静态规则系统，可能 conservative。

然后说明这些限制不否定项目价值：

The goal of this course project is not to solve all scientific code repair problems, but to build a reproducible and interpretable agentic repair workflow with explicit evaluation, safety boundaries, and benchmark-driven analysis.
15. 文档网站建议

前端同学可以做一个轻量 documentation website，但不要做复杂 web dashboard。

推荐：

Material for MkDocs

网站导航建议：

Home
Research Questions
Architecture
Benchmark
Experiment Protocol
Results
Failure Taxonomy
Safety Review
Ablation Study
Demo Guide
Frontend Handoff
Final Status

网站定位：

Documentation and demonstration site for SciCodePilot.

不要让前端同学：

重写 BackendController
重写 Textual frontend
引入数据库
做复杂交互 dashboard
依赖真实 API key
16. 下一位 GPT 应该如何继续

新 GPT 接手后，第一步应该复述当前状态，不要建议继续堆功能。

建议新 GPT 的优先任务顺序：

1. 先设计 M23：Final Report Assets
2. 整理最终报告 outline
3. 生成 Method / Experiment / Results 初稿
4. 生成系统架构图和事件流图
5. 帮助前端同学做 docs website 内容组织
6. 帮助准备 PPT story
7. 最后再考虑是否需要补 1–2 个 challenge task，但默认不建议

新 GPT 需要记住：

M20-M22 已经让项目具备研究评价能力。
现在不要再以“继续写代码”为主。
现在要把项目包装成一个完整、有研究问题、有实验、有消融、有安全分析、有展示的网站/报告/PPT。