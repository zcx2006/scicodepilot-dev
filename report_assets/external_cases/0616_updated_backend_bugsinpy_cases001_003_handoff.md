# SciCodePilot 更新后 BugsInPy 三个 Case 测试交接文档

## 1. 交接目的

本文档用于向 SciCodePilot 后端负责人交接更新后分支在三个真实 BugsInPy `youtube-dl` case 上的回归测试结果：

- `case_001`：youtube-dl Bug 17
- `case_002`：youtube-dl Bug 11
- `case_003`：youtube-dl Bug 29

本轮依据原交接要求，验证以下完整链路：

```text
before failed
→ specialized diagnosis
→ specialized FailureMemory
→ PatchPlan
→ Safety Review
→ isolated workspace apply
→ after verification
→ patch_success
```

只有同时满足以下条件，才标记为 `patch_success`：

```text
before_return_code != 0
after_return_code == 0
patch_applied == true
original_repo_mutated == false
```

本轮三个 case 均满足上述条件。

---

## 2. 测试环境与目录

### 根目录

```text
D:\Git\My_Git_Project\BugsInPy_0616
```

### 后端分支目录

```text
scicodepilot-case001
→ backend-external-repair-case001
→ 用于 Bug 17

scicodepilot-case002-003
→ backend-external-repair-cases002-003
→ 用于 Bug 11、Bug 29
```

### BugsInPy 工作目录

```text
D:\Git\My_Git_Project\BugsInPy_0616\BugsInPy_Workdir
```

### 实验结果目录

```text
D:\Git\My_Git_Project\BugsInPy_0616\external_experiments_0616\branch_results
```

---

## 3. 更新前后总体对比

| 能力 | 更新前 main | 更新后分支 |
|---|---|---|
| AssertionError 分类 | `unsupported_external_failure` | `external_assertion_failure` |
| TypeError 分类 | `unsupported_external_failure` | `external_type_error` |
| FailureMemory | 通用兜底 | specialized |
| PatchPlan | `no_op` | 有效 PatchPlan |
| Safety Review | 无有效补丁 | approved / low risk |
| patch apply | 未打通 | isolated workspace 中成功 |
| after verification | 无 | `after_return_code = 0` |
| final status | unsupported / no-op | `patch_success` |

本轮更新已打通：

```text
识别 → 分析 → 规划 → 安全审查 → 隔离应用 → 修复后验证
```

---

# 4. Case 001：youtube-dl Bug 17

## 基本信息

```text
Case ID: case_001
Project: youtube-dl
Bug ID: 17
Buggy commit: 4bf22f7a1014c55e3358b5a419945071b152eafc
Backend branch: backend-external-repair-case001
Python: 3.13.5
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616\BugsInPy_Workdir\case_001_bug17\youtube-dl
```

## 原始问题

目标函数：

```python
cli_bool_option
```

错误逻辑：

```python
param = params.get(param)
assert isinstance(param, bool)
```

配置 key 缺失时：

```text
params.get(...) → None
→ assert isinstance(None, bool)
→ AssertionError
```

## 最小复现命令

```bash
python -c "from youtube_dl.utils import cli_bool_option; print(cli_bool_option({}, '--no-check-certificate', 'nocheckcertificate'))"
```

修复前：

```text
before_return_code = 1
raw_error_type = AssertionError
```

## Diagnosis

```text
detected_failure_type = external_assertion_failure
failure_memory_generated = true
failure_memory_specialized = true
```

结构化定位：

```text
file = youtube_dl/utils.py
function = cli_bool_option
line = 2736
assertion = assert isinstance(param, bool)
```

FailureMemory 正确识别：

```text
dict.get(...) 在 key 缺失时返回 None，
随后进入 bool-only assertion。
```

## Repair-plan

```text
patch_plan_generated = true
plan_type = PatchPlan
patch_applied = false
final_status = repair_plan_only
safety_review_approved = true
risk = low
```

生成补丁：

```diff
 param = params.get(param)
+if param is None:
+    return []
 assert isinstance(param, bool)
```

## Repair

```text
before_return_code = 1
after_return_code = 0
patch_applied = true
original_repo_mutated = false
final_status = patch_success
```

结论：

```text
Bug 17 = patch_success
```

---

# 5. Case 002：youtube-dl Bug 11

## 基本信息

```text
Case ID: case_002
Project: youtube-dl
Bug ID: 11
Buggy commit: b568561eba6f4aceb87419e21aba11567c5de7da
Backend branch: backend-external-repair-cases002-003
Python: 3.13.5
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616\BugsInPy_Workdir\case_002_bug11\youtube-dl
```

## 原始问题

目标函数：

```python
str_to_int
```

错误逻辑：

```python
if int_str is None:
    return None
int_str = re.sub(r'[,\.\+]', '', int_str)
```

整数输入时：

```text
str_to_int(123)
→ re.sub(..., 123)
→ TypeError
```

## 最小复现命令

```bash
python -c "from youtube_dl.utils import str_to_int; print(str_to_int(123))"
```

修复前：

```text
before_return_code = 1
raw_error_type = TypeError
```

错误信息：

```text
TypeError: expected string or bytes-like object, got 'int'
```

## Diagnosis

```text
detected_failure_type = external_type_error
failure_memory_generated = true
failure_memory_specialized = true
```

FailureMemory 正确识别：

```text
非字符串输入进入 regex/string processing，
而实现只对 None 做特殊处理。
```

## Repair-plan

```text
patch_plan_generated = true
plan_type = PatchPlan
patch_applied = false
final_status = repair_plan_only
safety_review_approved = true
risk = low
```

生成补丁：

```diff
-if int_str is None:
-    return None
+if not isinstance(int_str, compat_str):
+    return int_str
```

## Repair

```text
before_return_code = 1
after_return_code = 0
patch_applied = true
original_repo_mutated = false
final_status = patch_success
```

修复后：

```text
str_to_int(123) → 123
```

结论：

```text
Bug 11 = patch_success
```

---

# 6. Case 003：youtube-dl Bug 29

## 基本信息

```text
Case ID: case_003
Project: youtube-dl
Bug ID: 29
Buggy commit: c514b0ec655b23e7804eb18df04daa863d973f32
Backend branch: backend-external-repair-cases002-003
Python: 3.11.9
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616\BugsInPy_Workdir\case_003_bug29\youtube-dl
```

Python 3.11 虚拟环境：

```text
D:\Git\My_Git_Project\BugsInPy_0616\venvs\case_003_bug29_py311
```

## 环境说明

Python 3.13 无法运行该历史版本，因为旧版 youtube-dl 使用：

```python
import pipes
```

`pipes` 已从 Python 3.13 移除，因此使用 Python 3.11.9。虚拟环境通过：

```bash
py -3.11 -m venv --without-pip ...
```

创建，并确认：

```text
pipes import OK
```

## 原始问题

目标函数：

```python
unified_strdate
```

错误逻辑：

```python
return compat_str(upload_date)
```

无效日期字符串导致：

```text
upload_date = None
compat_str(None) → 'None'
```

即返回字符串 `'None'`，而非 Python `None`。

## 最小复现命令

```bash
python -c "from youtube_dl.utils import unified_strdate; assert unified_strdate('not-a-date') is None"
```

修复前：

```text
before_return_code = 1
raw_error_type = AssertionError
```

人工验证：

```text
unified_strdate('not-a-date') → 'None'
```

## Diagnosis

```text
detected_failure_type = external_assertion_failure
failure_memory_generated = true
failure_memory_specialized = true
interpreter = Python 3.11.9
```

FailureMemory 正确识别：

```text
invalid date string 使 upload_date 保持 None，
随后 compat_str(None) 产生字符串 'None'。
```

## Repair-plan

```text
patch_plan_generated = true
plan_type = PatchPlan
patch_applied = false
final_status = repair_plan_only
safety_review_approved = true
risk = low
```

生成补丁：

```diff
-return compat_str(upload_date)
+if upload_date is not None:
+    return compat_str(upload_date)
```

## Repair

```text
before_return_code = 1
after_return_code = 0
patch_applied = true
original_repo_mutated = false
final_status = patch_success
```

结论：

```text
Bug 29 = patch_success
```

---

# 7. 三个 Case 汇总

| Case | Bug | Python | Raw Error | SciCodePilot Failure Type | FailureMemory | PatchPlan | Patch Applied | Before RC | After RC | Original Repo Mutated | Final Status |
|---|---:|---|---|---|---|---|---|---:|---:|---|---|
| case_001 | 17 | 3.13.5 | AssertionError | external_assertion_failure | specialized | yes | true | 1 | 0 | false | patch_success |
| case_002 | 11 | 3.13.5 | TypeError | external_type_error | specialized | yes | true | 1 | 0 | false | patch_success |
| case_003 | 29 | 3.11.9 | AssertionError | external_assertion_failure | specialized | yes | true | 1 | 0 | false | patch_success |

统计：

```text
总 case 数：3
before failed：3
specialized diagnosis：3
specialized FailureMemory：3
PatchPlan generated：3
patch applied：3
after passed：3
patch_success：3
```

---

# 8. 当前仍发现的问题

## diagnosis 模式 final_status 命名不准确

`diagnosis` 模式下仍显示：

```text
final_status = patch_failed
```

但 diagnosis 阶段并未尝试 patch。建议改为：

```text
diagnosis_success_only
```

或：

```text
diagnosis_completed
```

## 默认输出目录容易与统一实验目录脱节

命令若漏写 `--output-dir`，结果会保存到：

```text
scicodepilot-*/outputs/external_smoke/<timestamp>
```

建议 CLI 更明显提示当前使用默认输出目录。

## `outputs/external_smoke` 文件/目录冲突

`scicodepilot-case001` 下载后，`outputs/external_smoke` 是 1 字节普通文件，而脚本将其视为目录，首次运行触发 `FileExistsError`。

建议：

- 删除该普通文件；
- 改为真实目录并放置 `.gitkeep`；
- 或统一使用 `outputs/external_smoke_outputs`。

## Bug 29 需要特定 Python 版本

建议继续保留并完善：

```text
per-case interpreter
python version recording
environment failure 与 target failure 分离
```

---

# 9. 推荐答辩展示

## 首选：Bug 17

原因：

- 问题简单；
- FailureMemory 可读；
- Patch 仅两行；
- before / after 直观；
- 完整体现 SciCodePilot 修复闭环。

## 备选：Bug 11

展示：

```text
TypeError parser + 类型保护修复
```

## 补充：Bug 29

展示：

```text
Python 3.11 指定解释器 + 返回值语义错误
```

---

# 10. 建议发送给后端的文件

## 必发

1. 本交接文档：

```text
0616_updated_backend_bugsinpy_cases001_003_handoff.md
```

2. 三个最终摘要：

```text
branch_results\case001\bug17_final_summary.md
branch_results\cases002_003\bug11_final_summary.md
branch_results\cases002_003\bug29_final_summary.md
```

3. 每个 case 的 diagnosis、repair-plan、repair 三阶段 `summary.md` 和 `summary.json`。

### Bug 17

```text
case001\outputs\bug17_diagnosis\summary.md
case001\outputs\bug17_diagnosis\summary.json
case001\outputs\bug17_repair_plan\summary.md
case001\outputs\bug17_repair_plan\summary.json
case001\outputs\bug17_repair\summary.md
case001\outputs\bug17_repair\summary.json
```

### Bug 11

```text
cases002_003\outputs\bug11_diagnosis\summary.md
cases002_003\outputs\bug11_diagnosis\summary.json
cases002_003\outputs\bug11_repair_plan\summary.md
cases002_003\outputs\bug11_repair_plan\summary.json
cases002_003\outputs\bug11_repair\summary.md
cases002_003\outputs\bug11_repair\summary.json
```

### Bug 29

```text
cases002_003\outputs\bug29_diagnosis\summary.md
cases002_003\outputs\bug29_diagnosis\summary.json
cases002_003\outputs\bug29_repair_plan\summary.md
cases002_003\outputs\bug29_repair_plan\summary.json
cases002_003\outputs\bug29_repair\summary.md
cases002_003\outputs\bug29_repair\summary.json
```

## 建议发送

运行日志：

```text
bug17_diagnosis.log
bug17_repair_plan.log
bug17_repair.log

bug11_before.log
bug11_diagnosis.log
bug11_repair_plan.log
bug11_repair.log

bug29_diagnosis.log
bug29_repair_plan.log
bug29_repair.log
```

Parser 与环境证据：

```text
case001\logs\parser_search.log
cases002_003\logs\parser_search.log
Bug 29 Python 3.11 / pipes import OK 记录
```

## 不建议发送

```text
完整 workspace
完整 youtube-dl 源码副本
完整 Python 虚拟环境
__pycache__
```

这些体积较大，保留在本机即可。

---

# 11. 最终结论

```text
总共回归：3 个 BugsInPy 外部 case
before failed：3
specialized diagnosis：3
PatchPlan generated：3
patch applied：3
after passed：3
patch_success：3
```

最终结论：

> 后端新增的 external AssertionError / TypeError parser、specialized FailureMemory、PatchPlan、Safety Review、isolated patch apply 和 after verification 已在三个真实 BugsInPy youtube-dl case 上全部验证成功。三个 case 均从更新前的 unsupported/no-op 状态提升为完整 `patch_success`，可用于项目汇报与答辩展示。
