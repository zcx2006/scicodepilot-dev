# SciCodePilot × BugsInPy 三个外部 Case 完整交接文档

## 1. 交接目的

本文件用于向 SciCodePilot 后端负责人完整交接三个 BugsInPy 外部实验：

- `case_001`：youtube-dl Bug 17
- `case_002`：youtube-dl Bug 11
- `case_003`：youtube-dl Bug 29

实验目标是验证：

```text
真实外部仓库
→ 获取 buggy version
→ 手动复现 before failure
→ SciCodePilot diagnosis
→ FailureMemory
→ repair-plan
→ isolated workspace
→ patch apply
→ after verification
```

目前三个 case 均已完成：

```text
源码准备
→ before 复现
→ diagnosis
→ repair-plan
→ 安全边界验证
```

但均未进入有效 PatchPlan、patch apply 和 after verification。

---

# 2. 实验目录

根目录：

```text
D:\Git\My_Git_Project\Bugs_2nd_try
```

结构：

```text
Bugs_2nd_try
├─BugsInPy
├─scicodepilot-dev-main
├─BugsInPy_Workdir
│  ├─archives
│  ├─case_001_bug17
│  ├─case_002_bug11
│  └─case_003_bug29
└─external_experiments
   ├─logs
   ├─summaries
   ├─notes
   ├─codex_results
   └─scicodepilot_outputs
```

---

# 3. 工具和环境

## 3.1 BugsInPy

BugsInPy 当前版本通过 Bash 脚本使用：

```text
framework/bin/bugsinpy-checkout
framework/bin/bugsinpy-info
framework/bin/bugsinpy-test
framework/bin/bugsinpy-compile
```

不能使用：

```cmd
python -m bugsinpy
```

Git Bash 中确认：

```bash
bash framework/bin/bugsinpy-checkout --help
bash framework/bin/bugsinpy-info --help
```

## 3.2 SciCodePilot

使用：

```text
scripts/run_external_repo_smoke.py
```

参数：

```text
--repo-path
--command
--mode {diagnosis,repair-plan}
--copy-workspace
--output-dir
```

## 3.3 Python

- SciCodePilot：Python 3.13.5
- Bug 17：Python 3.13.5
- Bug 11：Python 3.13.5
- Bug 29：Python 3.11 虚拟环境

Bug 29 虚拟环境：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\venvs\case_003_bug29_py311
```

---

# 4. 源码获取方式

标准 `bugsinpy-checkout` 在 clone youtube-dl 时因网络和代理中断而停滞。

因此三个 case 均改用：

```text
GitHub exact commit ZIP archive
```

这保证源码对应正确 buggy commit，但没有 `.git` 元数据。

应记录：

```text
source_acquisition = GitHub commit ZIP archive
standard_checkout = stalled / not completed
git_metadata_available = false
```

---

# 5. Case 001：youtube-dl Bug 17

## 5.1 基本信息

```text
Bug ID: 17
Buggy commit: 4bf22f7a1014c55e3358b5a419945071b152eafc
Fixed revision: 5b232f46dcbdc805507c02edd4fd598f31d544d5
```

## 5.2 Bug 原因

函数：

```text
youtube_dl.utils.cli_bool_option
```

错误逻辑：

```python
param = params.get(param)
assert isinstance(param, bool)
```

缺失配置 key 时：

```text
param = None
→ AssertionError
```

正确修复：

```diff
+if param is None:
+    return []
```

## 5.3 原始测试

```bash
python -m unittest -q test.test_utils.TestUtil.test_cli_bool_option
```

结果：

```text
return code = 0
OK
```

原因：历史测试未覆盖缺失 key。

## 5.4 最小复现

```bash
python -c "from youtube_dl.utils import cli_bool_option; print(cli_bool_option({}, '--no-check-certificate', 'nocheckcertificate'))"
```

结果：

```text
AssertionError
before_return_code = 1
```

## 5.5 SciCodePilot 结果

```text
diagnosis = unsupported_external_failure
FailureMemory = generic fallback
repair-plan = no_op
valid PatchPlan = false
patch_applied = false
after_return_code = unavailable
original_repo_mutated = false
```

---

# 6. Case 002：youtube-dl Bug 11

## 6.1 基本信息

```text
Bug ID: 11
Buggy commit: b568561eba6f4aceb87419e21aba11567c5de7da
Fixed revision: 348c6bf1c1a00eec323d6e21ff7b9b12699afe04
```

## 6.2 Bug 原因

函数：

```text
youtube_dl.utils.str_to_int
```

错误逻辑：

```python
if int_str is None:
    return None
int_str = re.sub(..., int_str)
```

整数输入：

```python
str_to_int(123)
```

触发：

```text
TypeError: expected string or bytes-like object, got 'int'
```

正确修复：

```diff
-if int_str is None:
-    return None
+if not isinstance(int_str, compat_str):
+    return int_str
```

## 6.3 原始测试

```bash
python -m unittest -q test.test_utils.TestUtil.test_str_to_int
```

结果：

```text
return code = 0
OK
```

原因：历史测试只覆盖字符串。

## 6.4 最小复现

```bash
python -c "from youtube_dl.utils import str_to_int; print(str_to_int(123))"
```

结果：

```text
TypeError
before_return_code = 1
```

## 6.5 SciCodePilot 结果

```text
diagnosis = unsupported_external_failure
FailureMemory = generic fallback
repair-plan = no_op
valid PatchPlan = false
patch_applied = false
after_return_code = unavailable
original_repo_mutated = false
```

---

# 7. Case 003：youtube-dl Bug 29

## 7.1 基本信息

```text
Bug ID: 29
Buggy commit: c514b0ec655b23e7804eb18df04daa863d973f32
Fixed revision: 6a750402787dfc1f39a9ad347f2d78ae1c94c52c
```

## 7.2 Bug 原因

函数：

```text
youtube_dl.utils.unified_strdate
```

错误逻辑：

```python
return compat_str(upload_date)
```

无法解析的日期字符串导致：

```text
upload_date = None
compat_str(None) = 'None'
```

正确修复：

```diff
-return compat_str(upload_date)
+if upload_date is not None:
+    return compat_str(upload_date)
```

## 7.3 Python 3.13 环境问题

Python 3.13 下：

```text
ModuleNotFoundError: No module named 'pipes'
```

目标测试未执行。

## 7.4 Python 3.11 官方测试

```bash
python -m unittest -q test.test_utils.TestUtil.test_unified_dates
```

结果：

```text
return code = 0
OK
```

原因：历史测试只覆盖有效日期字符串。

## 7.5 最小复现

```bash
python -c "from youtube_dl.utils import unified_strdate; assert unified_strdate('not-a-date') is None"
```

结果：

```text
AssertionError
before_return_code = 1
```

## 7.6 SciCodePilot 结果

```text
diagnosis = unsupported_external_failure
FailureMemory = generic fallback
repair-plan = no_op
valid PatchPlan = false
patch_applied = false
after_return_code = unavailable
original_repo_mutated = false
```

---

# 8. 三个 Case 汇总

| Case | Bug | Raw Error | Before RC | Python | SciCodePilot Type | Repair Plan | Final Status |
|---|---:|---|---:|---|---|---|---|
| case_001 | 17 | AssertionError | 1 | 3.13 | unsupported_external_failure | no_op | unsupported_external_failure |
| case_002 | 11 | TypeError | 1 | 3.13 | unsupported_external_failure | no_op | unsupported_external_failure |
| case_003 | 29 | AssertionError | 1 | 3.11 | unsupported_external_failure | no_op | unsupported_external_failure |

---

# 9. 已验证可用的能力

SciCodePilot external smoke 已经可以：

1. 接收本地外部 repo；
2. 复制到 isolated workspace；
3. 运行指定命令；
4. 捕获 stdout / stderr；
5. 捕获 traceback；
6. 记录外部命令 return code；
7. 输出 summary.md；
8. 输出 summary.json；
9. 生成通用 FailureMemory；
10. 保证原始 repo 不被修改；
11. 允许通过命令传入不同 Python 解释器。

---

# 10. 当前核心缺口

三个 case 共同证明：

1. `AssertionError` 缺少 specialized parser；
2. `TypeError` 缺少 specialized parser；
3. 普通 Python 异常统一落入 `unsupported_external_failure`；
4. FailureMemory 只能生成通用兜底；
5. repair planner 只能生成 `no_op`；
6. 没有 source-level PatchPlan；
7. 没有 patch apply；
8. 没有 after verification；
9. 没有形成完整修复闭环。

---

# 11. 环境层缺口

Bug 29 额外说明：

1. 外部项目可能依赖旧 Python；
2. 需要区分环境失败和目标程序失败；
3. EnvDoctor 应识别解释器版本；
4. EnvDoctor 应识别已移除标准库；
5. external smoke 应显式记录 interpreter path；
6. 应允许 case 绑定 Python 环境；
7. `ModuleNotFoundError` 应生成 EnvRepairPlan，而不是混入普通代码错误。

---

# 12. 建议后端修改项

## 12.1 Parser

优先支持：

```text
AssertionError
TypeError
ValueError
KeyError
ImportError
ModuleNotFoundError
```

## 12.2 Traceback 结构化

提取：

```text
error_type
error_message
file_path
line_number
function_name
failing_expression
command
interpreter
workspace
```

## 12.3 FailureMemory

应生成具体：

```text
observed failure
root-cause hypothesis
affected symbol
repair target
verification command
```

## 12.4 PatchPlan

应生成源代码级修复计划，而不是 `no_op`。

## 12.5 Apply + Verify

目标流程：

```text
copy workspace
→ apply patch
→ rerun before command
→ after_return_code = 0
→ original repo unchanged
```

---

# 13. 三个 Case 可参考修复

## Bug 17

```diff
+if param is None:
+    return []
```

## Bug 11

```diff
-if int_str is None:
-    return None
+if not isinstance(int_str, compat_str):
+    return int_str
```

## Bug 29

```diff
-return compat_str(upload_date)
+if upload_date is not None:
+    return compat_str(upload_date)
```

---

# 14. 建议后端回归顺序

1. 先增加 `AssertionError` parser；
2. 重跑 Bug 17；
3. 重跑 Bug 29；
4. 增加 `TypeError` parser；
5. 重跑 Bug 11；
6. 检查 FailureMemory 是否具体；
7. 检查 PatchPlan 是否非 no-op；
8. 在 isolated workspace 应用；
9. 运行 after verification；
10. 确认 original repo 未修改。

---

# 15. 成功判定标准

只有同时满足：

```text
before_return_code != 0
patch_applied = true
after_return_code = 0
original_repo_mutated = false
```

才能记录：

```text
patch_success
```

当前三个 case 均不满足。

---

# 16. 当前最终状态

```text
Bug 17 = unsupported_external_failure
Bug 11 = unsupported_external_failure
Bug 29 = unsupported_external_failure
```

当前不是实验失败，而是明确定位了后端 external parser、FailureMemory、repair-plan、apply/verify 和环境管理的能力缺口。

---

# 17. 建议发送文件

## Case 001

```text
case_001_before.log
case_001_scicodepilot_diagnosis.log
case_001_scicodepilot_repair_plan.log
case_001_diagnosis/summary.md
case_001_diagnosis/summary.json
case_001_repair_plan/summary.md
case_001_repair_plan/summary.json
```

## Case 002

```text
case_002_before.log
case_002_scicodepilot_diagnosis.log
case_002_scicodepilot_repair_plan.log
case_002_diagnosis/summary.md
case_002_diagnosis/summary.json
case_002_repair_plan/summary.md
case_002_repair_plan/summary.json
```

## Case 003

```text
case_003_before.log
case_003_before_official.log
case_003_before_official_py311.log
case_003_scicodepilot_diagnosis.log
case_003_scicodepilot_repair_plan.log
case_003_diagnosis/summary.md
case_003_diagnosis/summary.json
case_003_repair_plan/summary.md
case_003_repair_plan/summary.json
```

不必发送完整 workspace。
