# SciCodePilot 外部 Benchmark：youtube-dl Bug 29 完整实验记录

## 1. 文档目的

本文档完整记录 `case_003 / youtube-dl Bug 29` 的实验过程，包含：

- BugsInPy 元数据读取
- Buggy commit 获取
- 源码下载与目录整理
- Python 3.13 环境问题
- Python 3.11 虚拟环境切换
- 官方测试结果
- 最小复现命令
- SciCodePilot diagnosis
- SciCodePilot repair-plan
- 最终结论与后端建议

本实验未修改 youtube-dl 原始源码，也未修改 SciCodePilot 后端。

---

## 2. 基本信息

```text
Case ID: case_003
Project: youtube-dl
Bug ID: 29
Buggy commit: c514b0ec655b23e7804eb18df04daa863d973f32
Fixed revision: 6a750402787dfc1f39a9ad347f2d78ae1c94c52c
Triggering test file: test/test_utils.py
```

BugsInPy 信息获取命令：

```bash
bash framework/bin/bugsinpy-info -p youtube-dl -i 29
```

源码下载地址：

```text
https://github.com/ytdl-org/youtube-dl/archive/c514b0ec655b23e7804eb18df04daa863d973f32.zip
```

源码目录：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_003_bug29\youtube-dl
```

源码获取方式：

```text
GitHub commit ZIP archive
```

标准 BugsInPy checkout 未使用，原因是完整 clone 先前因网络与代理中断而停滞。

---

## 3. Bug 29 的源码问题

BugsInPy 提供的补丁如下：

```diff
diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py
index 7b3f79141..d39f313a4 100644
--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -911,7 +911,8 @@ def unified_strdate(date_str, day_first=True):
         timetuple = email.utils.parsedate_tz(date_str)
         if timetuple:
             upload_date = datetime.datetime(*timetuple[:6]).strftime('%Y%m%d')
-    return compat_str(upload_date)
+    if upload_date is not None:
+        return compat_str(upload_date)
```

错误版本在日期字符串无法解析时：

```python
upload_date = None
return compat_str(upload_date)
```

会把 Python 的 `None` 转成字符串：

```python
'None'
```

正确行为应是直接返回：

```python
None
```

---

## 4. 原始测试内容

BugsInPy 指定测试：

```bash
python -m unittest -q test.test_utils.TestUtil.test_unified_dates
```

历史测试只覆盖可正常解析的日期字符串，例如：

```python
unified_strdate('December 21, 2010')
unified_strdate('8/7/2009')
unified_strdate('2012/10/11 01:56:38 +0000')
unified_strdate('25-09-2014')
```

没有覆盖无法解析的字符串，例如：

```python
'not-a-date'
```

因此，即使源码存在 Bug，官方测试也可能返回 `OK`。

---

## 5. Python 3.13 环境问题

第一次在 Python 3.13 下运行官方测试时，输出：

```text
ModuleNotFoundError: No module named 'pipes'
```

返回码：

```text
1
```

该失败发生在模块导入阶段：

```text
youtube_dl/utils.py
import pipes
```

因此：

```text
Bug 29 target test reached: no
Bug 29 reproduction confirmed: no
Failure layer: Python environment compatibility
```

这是环境兼容问题，不是 Bug 29 本身。

---

## 6. Python 3.11 虚拟环境

为避免修改源码，创建 Python 3.11 虚拟环境：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\venvs\case_003_bug29_py311
```

激活后：

```bash
source /d/Git/My_Git_Project/Bugs_2nd_try/venvs/case_003_bug29_py311/Scripts/activate
```

确认：

```text
Python 3.11
```

Python 3.11 下，旧版 youtube-dl 可以正常导入 `pipes`。

---

## 7. Python 3.11 下的官方测试

执行：

```bash
python -m unittest -q test.test_utils.TestUtil.test_unified_dates
```

结果：

```text
Ran 1 test in 0.039s
OK
```

返回码：

```text
0
```

说明：

```text
Python 3.11 environment compatibility: success
Official test result: passed
Official test triggered Bug 29: no
```

---

## 8. 最小复现过程

### 8.1 检查 `None` 输入

执行：

```bash
python -c "from youtube_dl.utils import unified_strdate; print(repr(unified_strdate(None)))"
```

结果：

```text
None
```

这是正确行为，因为源码前面已有：

```python
if date_str is None:
    return None
```

因此 `None` 不是 Bug 29 的触发输入。

### 8.2 使用无法解析的日期字符串

执行：

```bash
python -c "from youtube_dl.utils import unified_strdate; print(repr(unified_strdate('not-a-date')))"
```

错误版本会返回：

```text
'None'
```

即字符串，而不是 Python 空值。

### 8.3 使用断言制造可验证失败

执行：

```bash
python -c "from youtube_dl.utils import unified_strdate; assert unified_strdate('not-a-date') is None"
```

结果：

```text
AssertionError
```

返回码：

```text
1
```

这证明：

```text
Input: 'not-a-date'
Expected: None
Actual: 'None'
Raw error type: AssertionError
Before return code: 1
```

该命令可稳定重复。

---

## 9. SciCodePilot diagnosis

### 9.1 环境分工

SciCodePilot 自身由 Python 3.13 启动。

Bug 29 外部命令显式使用 Python 3.11：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\venvs\case_003_bug29_py311\Scripts\python.exe
```

### 9.2 diagnosis 命令

```bash
python scripts/run_external_repo_smoke.py \
  --repo-path "D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_003_bug29\youtube-dl" \
  --command "\"D:\Git\My_Git_Project\Bugs_2nd_try\venvs\case_003_bug29_py311\Scripts\python.exe\" -c \"from youtube_dl.utils import unified_strdate; assert unified_strdate('not-a-date') is None\"" \
  --mode diagnosis \
  --copy-workspace \
  --output-dir "D:\Git\My_Git_Project\Bugs_2nd_try\external_experiments\scicodepilot_outputs\case_003_diagnosis"
```

### 9.3 diagnosis 结果

```text
SciCodePilot script return code: 0
External command return code: 1
Raw error: AssertionError
SciCodePilot error type: unsupported_external_failure
Isolated workspace created: yes
Traceback captured: yes
FailureMemory generated: yes
FailureMemory specialized: no
Original repo modified: no
```

FailureMemory 为通用兜底内容：

```text
The command failed, but the current rule-based memory builder
has no specialized hypothesis for this error type.
```

---

## 10. SciCodePilot repair-plan

### 10.1 repair-plan 命令

```bash
python scripts/run_external_repo_smoke.py \
  --repo-path "D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_003_bug29\youtube-dl" \
  --command "\"D:\Git\My_Git_Project\Bugs_2nd_try\venvs\case_003_bug29_py311\Scripts\python.exe\" -c \"from youtube_dl.utils import unified_strdate; assert unified_strdate('not-a-date') is None\"" \
  --mode repair-plan \
  --copy-workspace \
  --output-dir "D:\Git\My_Git_Project\Bugs_2nd_try\external_experiments\scicodepilot_outputs\case_003_repair_plan"
```

### 10.2 repair-plan 结果

```text
SciCodePilot script return code: 0
External command return code: 1
SciCodePilot error type: unsupported_external_failure
Plan type: no_op
Valid PatchPlan generated: no
Patch applied: false
After return code: not available
Original repo modified: no
```

系统说明：

```text
unsupported_external_failure:
current system can only generate a diagnosis summary
or no-op plan for this external failure.
```

---

## 11. Bug 29 最终结论

```text
before_return_code = 1
raw_error_type = AssertionError
scicodepilot_failure_type = unsupported_external_failure
failure_memory_generated = true
failure_memory_specialized = false
patch_plan_generated = false
patch_applied = false
after_return_code = not available
original_repo_mutated = false
final_status = unsupported_external_failure
```

Bug 29 的第一轮实验已完成，但没有真正修复。

准确表述：

```text
diagnosis completed
repair-plan completed
actual repair not performed
```

---

## 12. 对后端的价值

Bug 29 除了再次暴露 `AssertionError` parser 缺失，还额外暴露：

1. 外部仓库可能需要特定 Python 版本；
2. 环境错误必须与目标 bug 错误分开；
3. EnvDoctor 应识别旧标准库模块兼容性；
4. external smoke 应支持显式指定解释器；
5. parser 不应只输出 `unsupported_external_failure`；
6. FailureMemory 应提取错误返回值与期望值；
7. repair planner 应生成源代码级 PatchPlan；
8. 需要支持 isolated workspace 中 apply + verify。

---

## 13. 建议后端优先改进

### 13.1 环境层

- 允许 case 指定 Python 解释器；
- 记录 interpreter path；
- 区分 environment failure 与 target failure；
- 针对 `ModuleNotFoundError` 生成 EnvRepairPlan。

### 13.2 parser 层

支持：

```text
AssertionError
TypeError
ValueError
KeyError
ImportError
ModuleNotFoundError
```

### 13.3 FailureMemory 层

Bug 29 应生成类似：

```text
Root cause:
unified_strdate converts unresolved upload_date=None
to string 'None' via compat_str.

Expected:
Return Python None when parsing fails.
```

### 13.4 repair 层

应生成类似 PatchPlan：

```diff
- return compat_str(upload_date)
+ if upload_date is not None:
+     return compat_str(upload_date)
```

并重新运行原始失败命令，验证：

```text
after_return_code = 0
```

---

## 14. 推荐发送给后端的文件

```text
case_003_bug29_info.log
case_003_source_acquisition.log
case_003_before_official.log
case_003_before_official_return_code.txt
case_003_before_official_py311.log
case_003_before_official_py311_return_code.txt
case_003_before.log
case_003_before_return_code.txt
case_003_before_repeat.log
case_003_before_repeat_return_code.txt
case_003_scicodepilot_diagnosis.log
case_003_scicodepilot_repair_plan.log
case_003_diagnosis/summary.md
case_003_diagnosis/summary.json
case_003_repair_plan/summary.md
case_003_repair_plan/summary.json
```

不必发送完整 workspace。
