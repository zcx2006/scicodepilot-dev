SciCodePilot GPT 设计交接文档：M13–M19
# 0. 项目基本信息

项目名：SciCodePilot

项目路径：

/home/zengl/projects/SciCodePilot

运行环境：

WSL Ubuntu
Conda 环境：scicodepilot-dev

长期约束：

所有命令必须在 WSL Ubuntu 中运行。
不要在 Windows PowerShell 中运行项目命令。
涉及 Python / pip 时，优先使用当前 conda 环境中的 python / pip。

进入项目的标准命令：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
# 1. 当前项目大方向

SciCodePilot 当前定位是：

面向科研算法复现、实验环境诊断、benchmark diagnosis/repair 的终端 Agent 后端与评测框架。

当前系统的核心不是单纯写一个 LLM demo，而是构建一个事件流驱动的科研代码诊断与修复 pipeline：

benchmark task
→ run command
→ capture stdout/stderr
→ parse error
→ build failure memory
→ propose patch or environment repair plan
→ safety review
→ optional confirmation
→ isolated workspace apply
→ verification
→ hidden evaluator
→ score.json
→ event stream to frontend

当前系统的核心边界：

BackendController 是前端稳定入口。
event_serializer 是前端稳定序列化入口。
benchmark task 定义系统能力边界。
FailureMemory / PatchPlanner / EnvDoctor / LLM Planner / Patch Safety Reviewer 是逐步增强的诊断与修复模块。

前端只应依赖：

from scicodepilot.backend.controller import BackendController
from scicodepilot.backend.event_serializer import event_to_dict, event_to_json

当前 frontend_contract.md 已明确：Textual 前端应把 BackendController 当作推荐 public API；事件流包含 EnvRepairPlanCreated、PatchReviewCreated 等新事件；可选 LLM planner 当前只通过 CLI 暴露，Textual public API 不暴露 use_llm_planner。

项目状态已经从“最小 demo”进入：

可评测
可扩展
可展示
有安全边界
有 benchmark suite
有 hidden evaluator
有 reference frontend
有可选 LLM 能力
# 2. M13–M19 总体路线

M13 到 M19 的演进逻辑是：

M13：扩展 benchmark 能力边界，从 3 个任务扩展到 6 个任务。
M14：引入 isolated workspace、hidden evaluator、score.json，避免污染原始 benchmark。
M15：新增 EnvDoctor，把 missing_module / missing_file 从源码 patch 中分离出来。
M16：实现 Textual reference frontend，把 BackendController 事件流真正接到 UI。
M17：新增可选 LLM PatchPlanner adapter，但默认仍走 deterministic rule-based PatchPlanner。
M18：扩展 LLM planner 为 multi-provider：mock / deepseek / gemini / openai / disabled。
M19：新增 Patch Safety Reviewer，让所有 PatchPlan 在确认或应用前先过静态安全审查。

这个路线的核心策略是：

先扩大 benchmark
再隔离运行环境
再区分源码错误和环境/数据错误
再提供最小前端展示
再接可选 LLM
最后补安全审查

因此，GPT 在本阶段一直避免让项目过早进入 OpenHands / LangGraph / 复杂 Agent graph，而是优先保证：

后端接口稳定
benchmark 可复现
patch 有确认机制
workspace 不污染原始任务
LLM 不破坏主路径
所有新增功能有测试
# 3. M13 设计交接：benchmark 扩展到 6 个任务
## 3.1 设计目标

M13 的目标是把 SciCodePilot 从“小 demo”推进到“像 benchmark system”。

M12 之前只有 3 个任务：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_missing_module_003

这对展示 MVP 足够，但作为课程项目或加分项，看起来还不够像一个完整 benchmark suite。

因此 M13 设计为新增 3 个任务：

repair_missing_file_004
repair_entrypoint_error_005
repair_label_shape_006

扩展后当前 6 个任务为：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_missing_module_003
repair_missing_file_004
repair_entrypoint_error_005
repair_label_shape_006
## 3.2 任务分类

支持自动 patch 的任务：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_entrypoint_error_005
repair_label_shape_006

保持 diagnosis-only 的任务：

repair_missing_module_003
repair_missing_file_004
## 3.3 为什么 missing_module / missing_file 不直接自动修

当时的设计判断是：

missing_module 是依赖/环境问题。
missing_file 是数据集/配置文件缺失问题。

它们不应该被普通 PatchPlanner 通过“改源码”伪装修复，例如：

删除 import
try/except 吃掉异常
创建假数据文件
跳过数据读取

这些做法会破坏科研复现实验的真实性。

因此 M13 先将它们保持为 diagnosis-only，为后续 M15 EnvDoctor 留出空间。

## 3.4 M13 prompt 策略

给 Codex 的 prompt 重点是：

新增 3 个 benchmark task。
扩展 TracebackParser。
扩展 FailureMemoryBuilder。
扩展 PatchPlanner。
扩展 suite runner 测试。
确保 pytest 全部通过。
确保原始 benchmark bug 不被永久修复。

M13 还要求保持：

BackendController public API 不变。
mode 仍然是 diagnosis / repair。
前端仍只调用 BackendController 和 event_serializer。
## 3.5 为什么 BackendController public API 必须不变

从 M12 开始，BackendController 已经被定义为前端稳定接口。如果 M13 为了扩展 benchmark 改动 public API，会导致前端同学无法并行工作。

因此所有新增能力都必须在内部 runner / planner / evaluator 中扩展，而不是破坏：

BackendController.list_tasks()
BackendController.get_task(task_id)
BackendController.run_task(task_id, mode, confirm_apply=False)
## 3.6 状态来源原则

M13 开始强调：

pytest 结果和 suite runner 结果比聊天记忆更可靠。

原因是 GPT 对话可能总结遗漏，但代码仓库中的测试结果、suite summary、输出 JSON 才是项目真实状态。

M13 完成时用户汇报：

pytest -q: 65 passed
diagnosis suite: total_tasks=6, diagnosis_pass_count=6
repair --confirm-apply: patch_applied_count=4, verification_success_count=4
# 4. M14 设计交接：workspace isolation / hidden evaluator / score.json
## 4.1 设计目标

M14 的目标是把 repair/evaluation 从直接操作原始 benchmark repo，改成在 isolated workspace 中执行。

M13 之前，即使 repair runner 会用 try/finally 恢复原始 bug，它仍然会临时修改：

benchmark/tasks/*/repo

这在 benchmark 设计上不够干净。

M14 后，流程变为：

benchmark 原始 repo
→ copy to isolated workspace
→ run diagnosis / patch / verification in workspace
→ hidden evaluator writes score.json
→ 原始 benchmark repo 永远不被修改
## 4.2 workspace 路径规则

workspace 根路径规则：

outputs/workspaces/<run_id>/<task_id>/

workspace repo 路径：

outputs/workspaces/<run_id>/<task_id>/repo

M14 要求：

original command 在 workspace_repo_dir 中运行。
PatchPlanner 读取 workspace 中的 train.py。
PatchApplier 修改 workspace 中的目标文件。
verification 在 workspace_repo_dir 中运行。
hidden evaluator 在 workspace_repo_dir 中运行。
## 4.3 为什么不能继续临时修改原始 repo

即使有恢复逻辑，也可能遇到：

进程中断
异常未捕获
并发运行
测试失败中途退出
手动终止

这些都会导致 benchmark 原始 bug 被污染。

课程展示中，isolated workspace 更容易解释：

原始 benchmark 是只读任务定义。
每次 run 都在独立 workspace 中完成。
repair 结果通过 hidden evaluator 评分。
## 4.4 hidden evaluator 为什么先做最小版本

M14 的 hidden evaluator 当前是最小版本：

运行 task.entry_command
return_code == 0 → success=True, score=1.0
return_code != 0 → success=False, score=0.0
写入 score.json

原因是当前重点是把评测框架结构打通，而不是立即实现复杂 hidden tests。

这给后续保留扩展空间：

hidden unit tests
score rubric
output comparison
functional correctness checks
multi-command evaluation
## 4.5 score.json 的作用

score.json 是每个 workspace 的结构化评测产物。

字段来自 ScoreResult，包括：

task_id
success
score
verification_command
return_code
message
score_path
checks

它让 suite runner 可以聚合：

scored_task_count
total_score
average_score
score_path
## 4.6 M14 对后续展示的意义

M14 是重要加分点，因为它把项目从“脚本修复 demo”升级为：

benchmark evaluation framework

报告中可以写：

Each repair trial is executed in an isolated workspace copied from the original benchmark repository. This prevents benchmark contamination and enables reproducible evaluation through score.json artifacts.

M14 完成时用户汇报：

pytest -q: 68 passed
repair --confirm-apply:
patch_applied_count=4
verification_success_count=4
scored_task_count=4
average_score=1.0
# 5. M15 设计交接：EnvDoctor / DataDoctor
## 5.1 设计目标

M15 的目标是专门处理：

repair_missing_module_003
repair_missing_file_004

也就是将环境/数据问题从源码 patch 中分离出来。

M15 不应让 PatchPlanner 伪造修复，而是新增：

EnvDoctor
→ EnvRepairPlan
→ EnvRepairPlanCreated event
## 5.2 为什么 EnvDoctor 不是普通 PatchPlanner

普通 PatchPlanner 处理的是源码错误，例如：

tensor shape mismatch
dtype mismatch
entrypoint typo
label shape mismatch

这些可以通过修改源码修复。

EnvDoctor 处理的是：

dependency missing
dataset/config file missing

这类问题需要用户安装依赖、下载数据、放置文件、检查路径，而不是直接改源码。

## 5.3 为什么不自动 pip install

M15 明确要求：

不要自动执行 pip install。
不要自动执行 conda install。
不要修改用户环境。

原因：

安装依赖有安全风险。
可能改变用户 conda 环境。
可能需要网络、权限、版本选择。
可能破坏已有环境。

后续如果要做自动环境修复，必须新增确认机制。

## 5.4 为什么不自动创建缺失文件

M15 同样要求：

不要自动创建缺失数据文件。
不要伪造 placeholder dataset。

原因：

科研复现中，缺数据文件通常意味着 dataset 未下载或路径配置错误。
创建假文件会让程序“跑通”但结果无意义。
## 5.5 EnvRepairPlan 字段

M15 实际完成的 EnvRepairPlan 字段为：

task_id
error_type
issue_category
summary
evidence
suggested_actions
verification_command
confidence
requires_user_action

其中：

missing_module → issue_category = dependency
missing_file   → issue_category = data
## 5.6 missing_module 如何提取模块名

从 evidence 中匹配类似：

ModuleNotFoundError: No module named 'xxx'

提取：

xxx

并生成建议验证命令：

python -c "import xxx"
## 5.7 missing_file 如何提取文件路径

从 evidence 中匹配类似：

FileNotFoundError: [Errno 2] No such file or directory: 'data/train.csv'

提取：

data/train.csv

并在 suggested_actions 中提示用户检查、下载或放置该文件。

## 5.8 repair advice 展示方式

M15 设计上建议将 advice 展示为：

环境/数据修复卡片
建议检查项
建议命令
用户需要手动处理

前端事件为：

EnvRepairPlanCreated

UI 映射为：

EnvRepairPlanCreated -> environment/data repair card
## 5.9 是否建议新增 EnvDiagnosisCreated 事件

本对话实际采用的是：

EnvRepairPlanCreated

没有新增 EnvDiagnosisCreated。如果后续 M20 以后想把“环境诊断”和“环境修复建议”分开，可以新增 EnvDiagnosisCreated，但当前不必。

## 5.10 为什么 EnvDoctor 要接入 runner / suite / frontend_contract

因为 EnvDoctor 不是孤立工具，它必须体现在完整用户体验中：

repair runner 需要 emit EnvRepairPlanCreated
suite runner 需要统计 env_repair_plan_count
frontend_contract 需要告诉前端如何展示
Textual frontend 需要不因无 patch 而崩溃

M15 完成时用户汇报：

pytest -q: 75 passed
repair suite:
patch_plan_count=4
env_repair_plan_count=2
repair --confirm-apply:
patch_applied_count=4
verification_success_count=4
scored_task_count=4
env_repair_plan_count=2
average_score=1.0
5.11 BackendController public API

M15 仍保持：

BackendController public API 不变。

EnvDoctor 通过事件流和 suite result 扩展，不通过改变前端入口扩展。

# 6. M16 设计交接：Textual reference frontend
## 6.1 实际 M16 内容

用户请求中曾提到“如果 M16 是围绕 EnvDoctor 集成……”，但本对话中实际 M16 是：

Textual 前端最小可运行版

不是 EnvDoctor 的后端集成。EnvDoctor 已在 M15 完成。

## 6.2 M16 目标

M16 的目标是实现一个 reference frontend：

Textual TUI
→ BackendController
→ async event stream
→ UI panels

它不是最终 UI，而是用于证明：

后端事件流可被真实前端消费。
PatchApprovalRequired / Confirm Apply 交互可跑通。
EnvRepairPlanCreated 不会导致前端崩溃。
PatchProposed / VerificationFinished / TaskFinished 等事件可展示。
## 6.3 新增文件

M16 用户汇报新增：

scicodepilot/frontend/__init__.py
scicodepilot/frontend/textual_app.py
scripts/run_textual_app.py
tests/test_textual_frontend_import.py
## 6.4 启动方式
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
python scripts/run_textual_app.py

smoke test：

python scripts/run_textual_app.py --smoke-test
## 6.5 给 Codex 的 prompt 重点

M16 prompt 的重点是：

前端只调用 BackendController / event_to_dict / event_to_json。
不要调用 ShellTool / PatchApplier / PatchPlanner / runners。
支持所有已有事件。
未知事件不崩溃，追加到 log panel。
Run 时清空旧日志。
运行中禁用 Run。
收到 PatchApprovalRequired 后启用 Confirm Apply。
Confirm Apply 通过重新运行同一任务 mode=repair, confirm_apply=True 实现。
## 6.6 Confirm Apply 语义

当前后端语义不是在同一个 async generator 中继续，而是：

第一次 repair:
run_task(task_id, mode="repair", confirm_apply=False)

收到 PatchApprovalRequired 后，用户点击 Confirm Apply:

第二次 repair:
run_task(task_id, mode="repair", confirm_apply=True)
## 6.7 测试策略

M16 没有要求复杂 UI snapshot 测试，只要求轻量测试：

textual_app 可以 import
SciCodePilotTextualApp 类存在
run_textual_app.py 存在
smoke test 通过

M16 完成时用户汇报：

pytest -q: 77 passed
diagnosis suite: diagnosis_pass_count=6
repair --confirm-apply: average_score=1.0
## 6.8 对前端同学的交接口径

M16 生成的是：

reference frontend

前端同学之后可以：

直接在 textual_app.py 上美化
或重写自己的 Textual UI

但必须遵守：

只调用 BackendController 和 event_serializer。
不要依赖内部 runner/tool。
# 7. M17 设计交接：可选 LLM PatchPlanner adapter
## 7.1 M17 目标

M17 的目标是新增：

LLM PatchPlanner adapter

但保持默认主路径仍然是 deterministic rule-based PatchPlanner。

M17 不做：

OpenHands
LangGraph
复杂 Agent graph
自动执行 LLM patch

只做：

ParsedError + FailureMemory + source file
→ LLMPatchPlanner
→ PatchPlan
## 7.2 为什么选择这个目标

M13–M16 已经让系统具备：

benchmark suite
workspace isolation
hidden evaluator
EnvDoctor
reference frontend

此时接 LLM 最合理，因为已有安全链路兜底：

PatchProposed
→ PatchApprovalRequired
→ confirm_apply
→ workspace apply
→ hidden evaluator
→ score.json

因此 LLM 只作为 planner，不直接修改文件。

## 7.3 涉及模块

M17 新增：

scicodepilot/llm/__init__.py
scicodepilot/llm/llm_client.py
scicodepilot/llm/llm_patch_planner.py
scicodepilot/llm/prompt_templates.py
scicodepilot/llm/README.md
tests/test_llm_client.py
tests/test_llm_patch_planner.py
## 7.4 GPT 给 Codex 的 prompt 策略

M17 prompt 要求：

新增 LLMClient 抽象接口。
实现 MockLLMClient。
实现 Disabled/Null client。
构造 JSON-only prompt。
LLMPatchPlanner 解析 JSON 转 PatchPlan。
invalid JSON / 低置信度 / 空 diff 返回 None。
use_llm_planner=False 默认走规则 planner。
use_llm_planner=True 时先尝试 LLM，失败 fallback 到规则 planner。
CLI 支持 --use-llm-planner。
## 7.5 稳定接口约束

M17 明确要求：

BackendController public API 不变。
不要把 use_llm_planner 暴露到 BackendController。
先通过 CLI 做后端实验功能。

原因是：

Textual frontend 当前 contract 不应被 LLM 实验功能污染。
## 7.6 验证要求

M17 要求验证：

pytest -q
python scripts/run_benchmark_suite.py --mode diagnosis
python scripts/run_benchmark_suite.py --mode repair --confirm-apply
SCICODEPILOT_LLM_MODE=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner

还要求检查原始 benchmark 未污染。

M17 完成时用户汇报：

pytest -q: 83 passed
普通 repair --confirm-apply: average_score=1.0
mock LLM repair --confirm-apply --use-llm-planner: average_score=1.0
# 8. M18 设计交接：LLM planner 多 provider
## 8.1 M18 目标

M18 的目标是将 M17 的 mock-only LLM adapter 扩展为 multi-provider：

mock
deepseek
gemini
openai
disabled

M18 完成后：

LLM planner 支持多 provider。
默认仍关闭。
BackendController public API 没变。
## 8.2 为什么要支持多 provider

用户有 Gemini / DeepSeek API，不一定有 OpenAI API。

同时，课程项目中“multi-provider LLM adapter”比只支持一个模型更有工程扩展性。

M18 还回答过：

ChatGPT Pro 不等于自动拥有 OpenAI API 额度。
OpenAI API 需要单独 API key 和 billing。

因此不应假设用户有 OpenAI API。

## 8.3 为什么默认仍关闭

LLM provider 可能出现：

无 API key
网络失败
额度不足
返回格式不稳定
输出非法 JSON
输出危险 patch

所以默认必须仍然是 deterministic rule-based PatchPlanner。

LLM planner 只能通过 CLI 和环境变量显式开启：

SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner
## 8.4 为什么不能破坏 deterministic PatchPlanner

benchmark 的主路径必须稳定可复现。

如果默认依赖 LLM：

pytest 可能不稳定
suite 结果不可复现
没有 key 时 demo 跑不了
评测结果依赖模型输出

因此 M18 的核心原则是：

LLM 是 optional add-on。
rule-based planner 是 benchmark baseline。
LLM 失败必须 fallback。
## 8.5 为什么不能改变 BackendController public API

LLM planner 是后端实验功能，不应该影响前端 public API。

当前前端 contract 仍要求只调用：

BackendController
event_to_dict
event_to_json

并且 frontend_contract.md 中明确：可选 LLM planner 当前只通过 CLI flags 暴露，Textual public API 不暴露 use_llm_planner。

## 8.6 llm_client 的职责

llm_client.py 的职责：

定义 LLMClient 接口。
实现 Mock / DeepSeek / Gemini / OpenAI / Disabled client。
从环境变量创建 provider client。
处理无 API key 的 fallback。
不让测试依赖真实 API。

环境变量：

SCICODEPILOT_LLM_PROVIDER=mock|deepseek|gemini|openai|disabled
SCICODEPILOT_DEEPSEEK_API_KEY=...
SCICODEPILOT_GEMINI_API_KEY=...
SCICODEPILOT_OPENAI_API_KEY=...
SCICODEPILOT_DEEPSEEK_MODEL=deepseek-chat
SCICODEPILOT_GEMINI_MODEL=gemini-1.5-flash
SCICODEPILOT_OPENAI_MODEL=gpt-4o-mini

兼容旧变量：

SCICODEPILOT_LLM_MODE=mock
## 8.7 llm_patch_planner 的职责

llm_patch_planner.py 的职责：

调用 LLMClient.complete(prompt)。
提取 JSON。
校验字段。
转为 PatchPlan。
无效时返回 None。
触发 fallback 到规则式 PatchPlanner。

M18 增强了 JSON extraction：

前后有解释文字、中间包含第一个 JSON object
invalid response 返回 None
## 8.8 README 应说明什么

scicodepilot/llm/README.md 应说明：

默认不使用 LLM。
mock provider 用于测试和离线 demo。
DeepSeek / Gemini / OpenAI 的环境变量配置方式。
不要把 API key 写入代码、测试、README 示例、shell history、日志。
ChatGPT Pro/Plus 与 OpenAI API billing 分开。
LLM patch 仍需要用户确认。
LLM patch 只在 isolated workspace 中应用。
真实 provider 失败会 fallback 到 rule-based planner。
## 8.9 测试应覆盖什么

M18 测试重点：

create_llm_client_from_env provider=mock。
旧 SCICODEPILOT_LLM_MODE=mock 兼容。
provider=disabled。
provider=deepseek/gemini/openai 但无 API key 不崩溃。
JSON extraction。
mock provider suite。
默认不设置 provider 时普通 repair suite 不变。

M18 完成时用户汇报：

pytest -q: 94 passed
ordinary repair --confirm-apply: average_score=1.0
mock provider repair --use-llm-planner: average_score=1.0
## 8.10 关于其他 API 的决策

用户问 KiloCode / Claude 等 API 是否需要现在接。

本 GPT 给出的决策是：

现在不建议继续接更多 provider。
M18 已经足够称为 multi-provider。
KiloCode / Claude / OpenRouter / Anthropic 可作为后续 backlog。
如果未来做，优先抽象成 OpenAI-compatible base_url provider。

理由：

继续加 provider 对当前展示增益不大。
容易引入配置、计费、网络和兼容性问题。
当前更重要的是 patch safety reviewer。
# 9. M19 设计交接：Patch Safety Reviewer / Patch Review Gate
## 9.1 M19 目标

M19 的目标是在所有 PatchPlan 进入确认或应用前，加一层静态安全审查：

PatchPlan
→ PatchSafetyReviewer
→ PatchReviewCreated
→ PatchApprovalRequired 或 PatchApplied
## 9.2 它解决了 M18 后的问题

M18 后系统已有 LLM planner。只要引入 LLM，就必须回答：

LLM 生成的 patch 会不会被无条件执行？

M19 的答案是：

不会。
所有 patch，不论来自规则 planner 还是 LLM planner，都必须经过 safety review。

这强化了项目的安全边界。

## 9.3 涉及文件或模块

M19 新增：

scicodepilot/review/__init__.py
scicodepilot/review/patch_review.py
scicodepilot/review/patch_safety_reviewer.py
tests/test_patch_safety_reviewer.py

修改：

RepairBenchmarkRunner
events/schema.py
RepairResult
suite result
frontend_contract.md
Textual app
event serializer tests
repair runner tests
suite runner tests
## 9.4 PatchReview 字段

M19 完成后 PatchReview 字段为：

task_id
error_type
target_file
approved
blocked
risk_level
reasons
warnings
reviewer
## 9.5 Reviewer 拦截风险

M19 reviewer 会阻止：

空 diff
绝对路径
../ 路径逃逸
workspace 外路径
benchmark/
reference/
outputs/
tests/
.git/
pyproject.toml
requirements.txt
多文件 diff
rm -rf
sudo
pip install
conda install
os.system
subprocess
eval(
exec(

弱错误类型对齐会升到 medium risk 并给 warning，但不一定 blocked。

## 9.6 GPT 给 Codex 的 prompt 重点

M19 prompt 的重点是：

新增 review 模块。
PatchSafetyReviewer 不执行 shell，不修改文件。
检查 target_file 是否相对路径且在 workspace 内。
检查 forbidden paths。
检查 dangerous strings。
检查单文件 patch。
检查 error_type 与 patch 内容的轻量一致性。
新增 PatchReviewCreated 事件。
PatchProposed 后必须 PatchReviewCreated。
blocked patch 不进入 confirmation，不 apply，不 hidden evaluator。
EnvDoctor 任务不生成 PatchPlan，所以不进入 review。
## 9.7 是否改变 BackendController public API

M19 不改变 BackendController public API。

仍然是：

list_tasks()
get_task(task_id)
run_task(task_id, mode, confirm_apply=False)
## 9.8 是否影响 benchmark suite

M19 影响 suite result，新增：

patch_review_count
patch_review_blocked_count
patch_review_approved
patch_review_blocked
patch_review_risk_level

预期当前 4 个可 patch 任务都 review approved：

patch_review_count=4
patch_review_blocked_count=0
## 9.9 是否影响 frontend_contract

M19 修改 frontend contract，新增：

PatchReviewCreated -> patch safety review card

并说明：

Every PatchProposed event is followed by PatchReviewCreated.
Blocked patch 不进入 confirmation / apply / hidden evaluator。
当前 reviewer 是 rule-based，后续可扩展 LLM reviewer。
## 9.10 是否影响 LLM planner 默认关闭策略

不影响。

LLM planner 仍然默认关闭。

M19 只是增加安全 gate：

rule-based PatchPlan → safety review
LLM PatchPlan → safety review
## 9.11 当前测试状态

M19 完成时用户汇报：

pytest -q: 105 passed
diagnosis suite:
  total_tasks=6
  diagnosis_pass_count=6
  patch_review_count=0

repair --confirm-apply:
  patch_plan_count=4
  patch_review_count=4
  patch_review_blocked_count=0
  patch_applied_count=4
  verification_success_count=4
  scored_task_count=4
  env_repair_plan_count=2
  average_score=1.0

mock LLM repair:
  patch_review_count=4
  patch_review_blocked_count=0
  average_score=1.0

原始 benchmark 未污染，仍保留：

classifier_expected_dim = 128
dtype=torch.float64
mainn()
batch_size + 1
# 10. 当前必须长期保持的设计约束
## 10.1 环境约束
所有命令必须在 WSL Ubuntu 中运行。
不要在 Windows PowerShell 里运行项目命令。
涉及 Python / pip 时，优先使用当前 conda 环境中的 python / pip。

标准进入项目：

cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
## 10.2 BackendController 约束

不要随便改：

BackendController.list_tasks()
BackendController.get_task(task_id)
BackendController.run_task(task_id, mode, confirm_apply=False)

mode 仍然是：

diagnosis
repair

不要改成：

diagnose

前端只依赖：

BackendController
event_to_dict
event_to_json

不要让前端直接调用：

ShellTool
PatchApplier
PatchPlanner
RepairBenchmarkRunner
DiagnosisBenchmarkRunner
## 10.3 Event schema 约束

event schema 可以增强，但已有事件不要删除、不要重命名。

当前重要事件包括：

TaskStarted
PlanCreated
StepStarted
CommandStarted
CommandOutput
CommandFinished
ErrorDetected
FailureMemoryCreated
EnvRepairPlanCreated
PatchProposed
PatchReviewCreated
PatchApprovalRequired
PatchApplied
VerificationStarted
VerificationFinished
TaskFinished

新增事件要同步更新：

Event union
event_serializer tests
frontend_contract.md
Textual app 如有必要
## 10.4 diagnosis / repair 行为约束
diagnosis mode 不应该修改代码。
repair mode confirm_apply=False 不应该 apply patch。
repair mode confirm_apply=True 才能 apply patch。
## 10.5 workspace 约束

M14 后：

apply patch 只能修改 workspace repo。
不能修改 benchmark 原始 repo。

workspace repo：

outputs/workspaces/<run_id>/<task_id>/repo

原始 benchmark repo 必须长期保持 bug 状态。

## 10.6 hidden evaluator 约束

当前 hidden evaluator 是最小实现：

主要基于 entry_command return_code。
score.json 当前不代表复杂 hidden tests。

后续可扩展，但不要在文档中夸大为完整 hidden test suite。

## 10.7 EnvDoctor 约束
missing_module 不应自动 pip install。
missing_file 不应自动创建文件。

除非未来明确设计：

EnvApprovalRequired
confirm_env_apply=True
environment sandbox

否则 EnvDoctor 只生成 plan。

## 10.8 LLM planner 约束
LLM planner 默认关闭。
deterministic PatchPlanner 仍然是 benchmark 主路径。
LLM planner 只提出 PatchPlan。
LLM 不直接改文件。
LLM 不执行 shell。
LLM 不安装依赖。
LLM 不创建缺失数据。
LLM 失败必须 fallback 到 rule-based planner。
10.9 Patch Safety 约束
所有 PatchPlan 都必须经过 PatchSafetyReviewer。
PatchReviewCreated 应出现在 PatchProposed 后。
blocked patch 不进入 PatchApprovalRequired。
blocked patch 不 apply。
blocked patch 不 hidden evaluator。
## 10.10 测试约束
新功能必须补测试。
pytest 和 suite runner 结果比聊天记忆更可靠。
# 11. 当前重要命令清单
## 11.1 进入项目
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev
## 11.2 跑全部测试
pytest -q

当前 M19 用户汇报期望：

105 passed
## 11.3 跑 diagnosis suite
python scripts/run_benchmark_suite.py --mode diagnosis

当前 M19 期望摘要：

total_tasks=6
diagnosis_pass_count=6
patch_review_count=0
## 11.4 跑 repair suite，不实际 apply
python scripts/run_benchmark_suite.py --mode repair

预期：

patch_plan_count=4
patch_applied_count=0
env_repair_plan_count=2
## 11.5 跑 repair suite，确认 apply
python scripts/run_benchmark_suite.py --mode repair --confirm-apply

当前 M19 期望：

patch_plan_count=4
patch_review_count=4
patch_review_blocked_count=0
patch_applied_count=4
verification_success_count=4
scored_task_count=4
env_repair_plan_count=2
average_score=1.0
## 11.6 跑 mock LLM repair suite
SCICODEPILOT_LLM_PROVIDER=mock python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner

当前 M19 期望：

patch_review_count=4
patch_review_blocked_count=0
average_score=1.0
## 11.7 跑 frontend contract demo
python scripts/run_frontend_contract_demo.py
## 11.8 跑 Textual reference frontend
python scripts/run_textual_app.py

smoke test：

python scripts/run_textual_app.py --smoke-test
## 11.9 检查原始 benchmark bug 未被污染
grep "classifier_expected_dim" benchmark/tasks/repair_tensor_shape_001/repo/train.py
grep "float64" benchmark/tasks/repair_dtype_mismatch_002/repo/train.py
grep "mainn" benchmark/tasks/repair_entrypoint_error_005/repo/train.py
grep "batch_size + 1" benchmark/tasks/repair_label_shape_006/repo/train.py

期望仍看到：

classifier_expected_dim = 128
dtype=torch.float64
mainn()
batch_size + 1
## 11.10 DeepSeek / Gemini LLM planner 示例

不要把 API key 写入代码或提交到 Git。

DeepSeek：

export SCICODEPILOT_LLM_PROVIDER=deepseek
export SCICODEPILOT_DEEPSEEK_API_KEY="你的key"
python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner

Gemini：

export SCICODEPILOT_LLM_PROVIDER=gemini
export SCICODEPILOT_GEMINI_API_KEY="你的key"
python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner

OpenAI：

export SCICODEPILOT_LLM_PROVIDER=openai
export SCICODEPILOT_OPENAI_API_KEY="你的key"
python scripts/run_benchmark_suite.py --mode repair --confirm-apply --use-llm-planner

注意：ChatGPT Pro/Plus 不等于自动拥有 OpenAI API 额度。OpenAI API 需要单独 API key 和 billing。

## 12. 当前项目状态快照

截至 M19，用户汇报的最新状态：

pytest -q: 105 passed

benchmark：

total_tasks=6

任务：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_missing_module_003
repair_missing_file_004
repair_entrypoint_error_005
repair_label_shape_006

支持自动 source-code patch：

repair_tensor_shape_001
repair_dtype_mismatch_002
repair_entrypoint_error_005
repair_label_shape_006

EnvDoctor / diagnosis-only：

repair_missing_module_003
repair_missing_file_004

当前主要模块能力：

Benchmark suite
TracebackParser
FailureMemory
Rule-based PatchPlanner
PatchApplier
WorkspaceManager
HiddenEvaluator
ScoreResult / score.json
EnvDoctor
Textual reference frontend
Optional LLM PatchPlanner
Multi-provider LLM client
PatchSafetyReviewer

当前 suite 关键结果：

diagnosis:
  total_tasks=6
  diagnosis_pass_count=6

repair --confirm-apply:
  patch_plan_count=4
  patch_review_count=4
  patch_review_blocked_count=0
  patch_applied_count=4
  verification_success_count=4
  scored_task_count=4
  env_repair_plan_count=2
  average_score=1.0

mock LLM repair:
  patch_review_count=4
  patch_review_blocked_count=0
  average_score=1.0
## 13. 后续 M20 的建议方向

M20 不建议继续盲目加功能。M20 应该优先做：

项目收束与展示工程化

推荐 M20 方向：

方向 A：Demo Story / One-command Showcase

目标：

让项目可以一条命令展示完整能力。

例如新增：

scripts/run_showcase.py

展示流程：

1. list tasks
2. diagnosis tensor_shape
3. repair tensor_shape without confirmation
4. repair tensor_shape with confirmation
5. EnvDoctor missing_module
6. mock LLM planner repair
7. patch safety review appears
8. print latest score.json path
9. print suite summary

优点：

适合课程展示。
适合录屏。
适合报告截图。
不会大改架构。
方向 B：Architecture Documentation / Report Assets

新增：

docs/architecture.md
docs/demo_guide.md
docs/milestones.md

内容：

系统架构图
事件流图
benchmark task 表
diagnosis vs repair vs env doctor
workspace isolation
LLM safety path
frontend contract

优点：

帮助写最终报告。
帮助前端同学理解系统。
降低新 GPT / Codex 交接成本。
方向 C：Frontend Polish Checklist

如果前端同学开始做 UI，M20 可以转向：

前端联调 checklist
事件样例 JSON
UI 状态机说明
Confirm Apply 交互规范
EnvRepairPlan 展示规范
PatchReviewCreated 展示规范

但如果前端还没开始，优先 A 或 B。

方向 D：LLM Reviewer

M19 已经有 rule-based safety reviewer。后续可以做：

Optional LLM reviewer

但不建议作为 M20 立刻做，除非项目展示时间充裕。因为 M19 已经提供安全 reviewer，M20 更适合收束展示。

建议选择

最推荐：

M20：Showcase + Documentation Pack

也就是：

scripts/run_showcase.py
docs/architecture.md
docs/demo_guide.md
docs/final_status.md

这样项目更像完整课程项目，而不是一直加内部模块。
