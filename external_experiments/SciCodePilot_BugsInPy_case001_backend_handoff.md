# SciCodePilot 外部 Benchmark / BugsInPy 实验阶段性汇报

## 1. 汇报目的

本文件用于向 SciCodePilot 后端负责人同步当前 BugsInPy 外部实验的完整过程、已获得结果、发现的问题以及下一步建议。

本次工作重点不是修改后端代码，而是验证真实外部 Python 仓库能否被 SciCodePilot 完成以下流程：

```text
外部仓库准备
→ bug 版本确认
→ 手动复现失败
→ SciCodePilot diagnosis
→ FailureMemory
→ repair-plan
→ isolated workspace
→ 后续 patch / verification
```

当前已完成第一个外部 case：`youtube-dl Bug 17`。

---

## 2. 本次实验环境

### 2.1 本地根目录

```text
D:\Git\My_Git_Project\Bugs_2nd_try
```

### 2.2 主要目录

```text
D:\Git\My_Git_Project\Bugs_2nd_try
├─BugsInPy
├─scicodepilot-dev-main
├─BugsInPy_Workdir
└─external_experiments
```

其中：

- `BugsInPy`：BugsInPy 框架、项目元数据、bug 信息、补丁和测试脚本。
- `scicodepilot-dev-main`：SciCodePilot 项目源码。
- `BugsInPy_Workdir`：实际外部仓库工作目录。
- `external_experiments`：保存日志、summary、SciCodePilot 输出和结果表。

### 2.3 命令行环境

BugsInPy 的 `framework/bin` 中工具是 Bash 脚本，因此最终使用 Git Bash，而不是 CMD 直接运行。

Git Bash 工作路径示例：

```bash
/d/Git/My_Git_Project/Bugs_2nd_try/BugsInPy
```

SciCodePilot 使用 Windows Python 运行：

```text
C:\Users\Liu\AppData\Local\Programs\Python\Python313\python.exe
```

Python 版本为 Python 3.13。

---

## 3. BugsInPy 工具确认过程

最初尝试使用：

```cmd
python -m bugsinpy --help
```

得到：

```text
No module named bugsinpy
```

后续确认当前 BugsInPy 不是通过 Python module 方式调用，而是通过以下 Bash 脚本：

```text
framework/bin/bugsinpy-checkout
framework/bin/bugsinpy-info
framework/bin/bugsinpy-test
framework/bin/bugsinpy-compile
```

在 Git Bash 中执行：

```bash
bash framework/bin/bugsinpy-checkout --help
bash framework/bin/bugsinpy-info --help
```

成功得到参数说明。

### 3.1 `bugsinpy-checkout` 参数

```text
-p project_name
-i bug_id
-v version_id
-w work_dir
```

其中：

- `-v 0`：buggy version
- `-v 1`：fixed version
- `-w`：工作目录

### 3.2 `bugsinpy-info` 参数

```text
-p project_name
-i bug_id
```

---

## 4. Codex 候选 case 筛选

使用 Codex 扫描了：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy\projects\youtube-dl\bugs
```

Codex 共整理了 20 个候选 case，并按以下标准进行分类：

- 优先：AssertionError、TypeError、ValueError、简单返回值错误、简单 config key 错误。
- 优先：本地离线单元测试。
- 优先：测试命令明确、修改范围小。
- 降低优先级：网络、外部 API、网站结构变化、大型 extractor 逻辑。
- 保留少量 `maybe` 和 `not_recommended` case 作为负面对照。

第一批建议 case：

1. `youtube-dl-17`
2. `youtube-dl-11`
3. `youtube-dl-29`

当前先完成了 Bug 17。

---

## 5. Case 001：youtube-dl Bug 17

### 5.1 基本信息

```text
Case ID: case_001
Project: youtube-dl
Bug ID: 17
```

执行：

```bash
bash framework/bin/bugsinpy-info -p youtube-dl -i 17
```

得到：

```text
Revision id:
5b232f46dcbdc805507c02edd4fd598f31d544d5

Buggy id:
4bf22f7a1014c55e3358b5a419945071b152eafc

Triggering test file:
test/test_utils.py
```

### 5.2 目标 bug

涉及函数：

```python
def cli_bool_option(params, command_option, param, true_value='true', false_value='false', separator=None):
    param = params.get(param)
    assert isinstance(param, bool)
    ...
```

BugsInPy 提供的修复补丁为：

```diff
 param = params.get(param)
+if param is None:
+    return []
 assert isinstance(param, bool)
```

说明 Bug 17 的核心问题是：

> 当配置字典中缺少指定 key 时，`params.get(param)` 返回 `None`，随后触发 `AssertionError`；正确行为应该是返回空列表 `[]`。

---

## 6. 源码获取过程

### 6.1 标准 checkout 尝试

使用 `bugsinpy-checkout` 克隆 `youtube-dl` 时，GitHub clone 长时间停在：

```text
Cloning into 'youtube-dl'...
```

由于网络和代理连接中断，标准 checkout 未完成。

### 6.2 备用获取方式

直接下载 Bug 17 对应的 buggy commit ZIP：

```text
https://github.com/ytdl-org/youtube-dl/archive/4bf22f7a1014c55e3358b5a419945071b152eafc.zip
```

解压到：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_001_bug17\youtube-dl
```

当前源码获取方式应记录为：

```text
Source acquisition: GitHub commit ZIP archive
Standard bugsinpy-checkout: interrupted / stalled
Exact buggy commit: 4bf22f7a1014c55e3358b5a419945071b152eafc
```

不能写成标准 BugsInPy checkout 成功。

---

## 7. Bug 17 测试确认

### 7.1 BugsInPy 提供的测试命令

Bug 17 的 `run_test.sh` 内容为：

```bash
python -m unittest -q test.test_utils.TestUtil.test_cli_bool_option
```

实际执行结果：

```text
Ran 1 test in 0.000s
OK
```

返回码：

```text
0
```

### 7.2 为什么原测试通过

检查 `test_cli_bool_option` 后发现，原测试只覆盖：

```python
{'nocheckcertificate': True}
{'nocheckcertificate': False}
```

没有覆盖以下缺失 key 的输入：

```python
{}
```

所以原始历史测试虽然通过，但并未触发 Bug 17。

### 7.3 最小复现命令

使用以下命令直接触发 Bug 17：

```bash
python -c "from youtube_dl.utils import cli_bool_option; print(cli_bool_option({}, '--no-check-certificate', 'nocheckcertificate'))"
```

实际结果：

```text
AssertionError
```

返回码：

```text
1
```

错误位置：

```text
youtube_dl/utils.py
cli_bool_option
assert isinstance(param, bool)
```

### 7.4 复现结论

```text
Raw error type: AssertionError
Before return code: 1
Stable reproduction: yes
Original source modified: no
```

需要特别说明：

- BugsInPy 自带 `run_test.sh` 返回 0。
- 最小复现命令返回 1。
- 最小复现输入依据来自 Bug 17 的 `bug_patch.txt` 所表达的缺失 key 行为。
- 没有修改 `youtube_dl/utils.py`。

---

## 8. SciCodePilot diagnosis 实验

### 8.1 使用脚本

SciCodePilot external smoke 脚本：

```text
scripts/run_external_repo_smoke.py
```

帮助信息确认参数：

```text
--repo-path
--command
--mode {diagnosis,repair-plan}
--copy-workspace
--output-dir
```

### 8.2 diagnosis 命令

```bash
python scripts/run_external_repo_smoke.py \
  --repo-path "D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_001_bug17\youtube-dl" \
  --command "python -c \"from youtube_dl.utils import cli_bool_option; print(cli_bool_option({}, '--no-check-certificate', 'nocheckcertificate'))\"" \
  --mode diagnosis \
  --copy-workspace \
  --output-dir "D:\Git\My_Git_Project\Bugs_2nd_try\external_experiments\scicodepilot_outputs\case_001_diagnosis"
```

### 8.3 diagnosis 结果

SciCodePilot 成功完成：

- 复制原始 repo 到 isolated workspace；
- 在 isolated workspace 中运行命令；
- 捕获 return code；
- 捕获 stderr；
- 捕获 traceback；
- 识别到 stderr 中存在 `AssertionError`；
- 生成 summary；
- 生成 FailureMemory 部分；
- 保证原始 repo 未被修改。

summary 关键内容：

```text
Return code: 1
Error type: unsupported_external_failure
Evidence:
- assert isinstance(param, bool)
- AssertionError
```

FailureMemory 内容为通用兜底：

```text
Root cause hypothesis:
The command failed, but the current rule-based memory builder has no specialized hypothesis for this error type.

Repair action:
Inspect the stderr evidence manually and extend the failure-memory rules if this error type should be supported.
```

### 8.4 diagnosis 结论

```text
Traceback captured: yes
Isolated workspace created: yes
FailureMemory generated: yes
FailureMemory specialized: no
SciCodePilot failure type: unsupported_external_failure
Original repo modified: no
```

---

## 9. SciCodePilot repair-plan 实验

### 9.1 repair-plan 命令

```bash
python scripts/run_external_repo_smoke.py \
  --repo-path "D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_001_bug17\youtube-dl" \
  --command "python -c \"from youtube_dl.utils import cli_bool_option; print(cli_bool_option({}, '--no-check-certificate', 'nocheckcertificate'))\"" \
  --mode repair-plan \
  --copy-workspace \
  --output-dir "D:\Git\My_Git_Project\Bugs_2nd_try\external_experiments\scicodepilot_outputs\case_001_repair_plan"
```

### 9.2 repair-plan 结果

summary 关键内容：

```text
Return code: 1
Error type: unsupported_external_failure
Plan type: no_op
```

系统说明：

```text
unsupported_external_failure:
current system can only generate a diagnosis summary or no-op plan for this external failure.
```

### 9.3 repair-plan 结论

```text
Valid PatchPlan generated: no
Plan type: no_op
Patch applied: false
After return code: not available
Original repo modified: no
```

`no_op` 不应视为有效 PatchPlan。

---

## 10. Case 001 最终结果

| 字段 | 结果 |
|---|---|
| case_id | case_001 |
| source | BugsInPy |
| project | youtube-dl |
| bug_id | 17 |
| source acquisition | GitHub commit ZIP |
| standard checkout | failed / stalled |
| standard run_test.sh | return code 0 |
| minimal reproduction | return code 1 |
| raw error type | AssertionError |
| traceback captured | yes |
| isolated workspace | yes |
| FailureMemory generated | yes |
| FailureMemory specialized | no |
| SciCodePilot failure type | unsupported_external_failure |
| repair plan | no_op |
| valid PatchPlan generated | no |
| patch applied | false |
| after return code | not available |
| original repo modified | no |
| final_status | unsupported_external_failure |

---

## 11. 当前后端瓶颈

通过 Case 001 可以确认：

### 11.1 已经打通的能力

SciCodePilot external smoke 当前已经能够：

1. 接收本地外部仓库路径；
2. 复制到 isolated workspace；
3. 在 workspace 中运行指定命令；
4. 捕获 stdout / stderr；
5. 捕获 traceback；
6. 记录 return code；
7. 输出 summary.md 和 summary.json；
8. 生成通用 FailureMemory；
9. 保证原始 repo 不被修改。

### 11.2 尚未打通的能力

当前主要缺口：

1. 外部 `AssertionError` 没有专门 parser；
2. 已捕获 `AssertionError`，但仍归类为 `unsupported_external_failure`；
3. FailureMemory 只能生成通用兜底内容；
4. 无法生成具体 root-cause hypothesis；
5. repair-plan 只能输出 `no_op`；
6. 尚未生成有效 PatchPlan；
7. 尚未应用 patch；
8. 尚未执行 after verification；
9. 尚未形成 `before failed → patch applied → after passed` 完整闭环。

---

## 12. 对后端的修改建议

建议后端优先支持以下能力：

### 优先级 1：增加外部 AssertionError parser

识别 stderr / traceback 中的：

```text
AssertionError
assert ...
```

建议生成类似：

```text
external_assertion_failure
```

或：

```text
assertion_failure
```

### 优先级 2：提取断言上下文

至少提取：

- 异常类型；
- 文件路径；
- 行号；
- 函数名；
- 断言表达式；
- 触发命令；
- 最上层业务调用；
- isolated workspace 路径。

Bug 17 示例：

```text
File: youtube_dl/utils.py
Function: cli_bool_option
Line: 2736
Assertion: assert isinstance(param, bool)
```

### 优先级 3：生成专门 FailureMemory

期望 FailureMemory 能形成：

```text
Observed failure:
AssertionError in cli_bool_option

Root cause hypothesis:
The requested configuration key is absent, params.get(param) returns None,
and the implementation asserts that the value must be bool.

Suggested repair:
Handle None before the bool assertion and return an empty argument list.
```

### 优先级 4：生成 source-level PatchPlan

Bug 17 可生成的 PatchPlan 目标：

```diff
 param = params.get(param)
+if param is None:
+    return []
 assert isinstance(param, bool)
```

### 优先级 5：支持 apply + verification

完成：

```text
copy workspace
→ apply patch in workspace
→ rerun original failing command
→ after return code 0
→ confirm original repo unchanged
```

---

## 13. 需要后端确认的问题

请后端负责人确认：

1. 当前是否计划支持外部 `AssertionError` parser？
2. external smoke 的 FailureMemory 是否只支持固定类型？
3. repair-plan 是否必须先依赖 specialized failure type？
4. 当前是否已有 external repair apply / verification 接口？
5. 是否需要实验负责人提供固定格式的 minimal reproduction command？
6. 后端后续修改完成后，是否需要重新运行 Case 001 验证？

---

## 14. 当前已有证据文件

建议查看以下文件：

```text
external_experiments/
├─logs/
│  ├─case_001_before.log
│  ├─case_001_before_return_code.txt
│  ├─case_001_before_repeat.log
│  ├─case_001_scicodepilot_diagnosis.log
│  ├─case_001_scicodepilot_repair_plan.log
│  └─case_001_source_acquisition.log
│
├─summaries/
│  ├─case_001_before_summary.md
│  └─case_001_scicodepilot_summary.md
│
├─scicodepilot_outputs/
│  ├─case_001_diagnosis/
│  │  ├─summary.md
│  │  ├─summary.json
│  │  └─workspace/
│  └─case_001_repair_plan/
│     ├─summary.md
│     ├─summary.json
│     └─workspace/
│
└─external_all_attempts.csv
```

向后端传递时不必传完整 `workspace`，优先发送：

```text
case_001_before.log
case_001_before_return_code.txt
case_001_scicodepilot_diagnosis.log
case_001_scicodepilot_repair_plan.log
case_001_diagnosis/summary.md
case_001_diagnosis/summary.json
case_001_repair_plan/summary.md
case_001_repair_plan/summary.json
case_001_scicodepilot_summary.md
external_all_attempts.csv
```

---

## 15. 阶段性结论

本次实验没有得到 patch success，但得到了一条非常明确的后端反馈：

```text
外部 AssertionError 能够被 runner 和 traceback 捕获，
isolated workspace 也正常工作，
但 parser 没有专门支持该错误类型，
FailureMemory 只能生成通用兜底结果，
repair-plan 只能输出 no_op，
因此无法进入 patch apply 和 after verification。
```

Case 001 的最终状态应记录为：

```text
unsupported_external_failure
```

不能记录为：

```text
diagnosis_success_only
repair_plan_only
patch_success
```

---

## 16. 下一步实验计划

实验负责人计划继续进行：

1. `youtube-dl Bug 11`
2. `youtube-dl Bug 29`
3. 对比不同错误类型是否都落入 `unsupported_external_failure`
4. 至少完成 3 个外部 case
5. 尝试寻找一个可以生成有效 PatchPlan 的 case
6. 后端修改 AssertionError parser 后重新回归 Case 001
7. 最终争取获得：

```text
before failed
→ specialized diagnosis
→ FailureMemory
→ PatchPlan
→ patch applied
→ after passed
```

---

## 17. 给后端负责人的简要结论

```text
我已完成第一例 BugsInPy 外部实验：youtube-dl Bug 17。

手动最小复现：
- raw error: AssertionError
- before return code: 1
- stable reproduction: yes

SciCodePilot diagnosis：
- traceback captured: yes
- isolated workspace: yes
- FailureMemory: generated, but generic
- detected type: unsupported_external_failure

SciCodePilot repair-plan：
- plan type: no_op
- valid PatchPlan: no
- patch applied: false
- after return code: unavailable

结论：
当前 external smoke runner 和隔离执行链路可用，
但 external AssertionError parser、专门 FailureMemory、
有效 PatchPlan 和 apply/verify 流程尚未打通。
```
