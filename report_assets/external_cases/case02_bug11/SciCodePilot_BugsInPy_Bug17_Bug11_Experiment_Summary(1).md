# SciCodePilot 外部 Benchmark 阶段性实验汇总（Bug 17 与 Bug 11）

## 1. 文档目的

本文件用于向 SciCodePilot 后端负责人汇报目前已完成的两个 BugsInPy 外部实验：

- `case_001`：youtube-dl Bug 17
- `case_002`：youtube-dl Bug 11

实验目标是验证真实外部 Python 仓库能否进入以下流程：

```text
获取 buggy 版本
→ 手动确认失败
→ SciCodePilot external diagnosis
→ FailureMemory
→ repair-plan
→ isolated workspace
→ 后续 patch / verification
```

本阶段不修改 SciCodePilot 后端，也不直接修改 BugsInPy 原始源码目录。

---

# 2. 实验环境

## 2.1 根目录

```text
D:\Git\My_Git_Project\Bugs_2nd_try
```

## 2.2 主要目录

```text
D:\Git\My_Git_Project\Bugs_2nd_try
├─BugsInPy
├─scicodepilot-dev-main
├─BugsInPy_Workdir
└─external_experiments
```

## 2.3 命令行与 Python

- BugsInPy 工具通过 Git Bash 运行。
- SciCodePilot 脚本使用 Windows Python。
- Python 版本：`Python 3.13.5`
- Python 路径：

```text
C:\Users\Liu\AppData\Local\Programs\Python\Python313\python.exe
```

---

# 3. BugsInPy 使用方式确认

最初尝试：

```cmd
python -m bugsinpy --help
```

得到：

```text
No module named bugsinpy
```

后续确认当前 BugsInPy 版本不是 Python module，而是 Bash 脚本工具：

```text
framework/bin/bugsinpy-checkout
framework/bin/bugsinpy-info
framework/bin/bugsinpy-test
framework/bin/bugsinpy-compile
```

Git Bash 中运行：

```bash
bash framework/bin/bugsinpy-checkout --help
bash framework/bin/bugsinpy-info --help
```

成功获得帮助信息。

---

# 4. 源码获取方式

标准 `bugsinpy-checkout` 需要从 GitHub 完整 clone youtube-dl，但网络和代理中断后 clone 长时间停滞，因此两个 case 均改用 GitHub 指定 commit ZIP。

实验记录中必须如实写为：

```text
Source acquisition: GitHub commit ZIP archive
Standard bugsinpy-checkout: stalled / not completed
Git metadata available: no
```

不能写成标准 checkout 成功。

---

# 5. Case 001：youtube-dl Bug 17

## 5.1 基本信息

```text
Case ID: case_001
Project: youtube-dl
Bug ID: 17
Buggy commit: 4bf22f7a1014c55e3358b5a419945071b152eafc
Fixed revision: 5b232f46dcbdc805507c02edd4fd598f31d544d5
Triggering test file: test/test_utils.py
```

源码目录：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_001_bug17\youtube-dl
```

## 5.2 Bug 17 的源码问题

错误版本代码：

```python
def cli_bool_option(params, command_option, param,
                    true_value='true', false_value='false', separator=None):
    param = params.get(param)
    assert isinstance(param, bool)
    if separator:
        return [command_option + separator + (true_value if param else false_value)]
    return [command_option, true_value if param else false_value]
```

BugsInPy 补丁：

```diff
 param = params.get(param)
+if param is None:
+    return []
 assert isinstance(param, bool)
```

当配置字典中缺少指定 key 时，`params.get(param)` 返回 `None`，随后触发 `AssertionError`。正确行为应为返回 `[]`。

## 5.3 BugsInPy 原始测试

```bash
python -m unittest -q test.test_utils.TestUtil.test_cli_bool_option
```

实际结果：

```text
Ran 1 test in 0.000s
OK
```

返回码：

```text
0
```

原因：原测试只覆盖 `True` 和 `False`，未覆盖空字典 `{}`。

## 5.4 最小复现命令

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

## 5.5 SciCodePilot diagnosis

```text
External command return code: 1
Raw error type: AssertionError
SciCodePilot error type: unsupported_external_failure
Traceback captured: yes
Isolated workspace created: yes
FailureMemory generated: yes
FailureMemory specialized: no
Original repo modified: no
```

## 5.6 SciCodePilot repair-plan

```text
Plan type: no_op
Valid PatchPlan generated: no
Patch applied: false
After return code: not available
```

## 5.7 最终状态

```text
final_status = unsupported_external_failure
```

---

# 6. Case 002：youtube-dl Bug 11

## 6.1 基本信息

```text
Case ID: case_002
Project: youtube-dl
Bug ID: 11
Buggy commit: b568561eba6f4aceb87419e21aba11567c5de7da
Fixed revision: 348c6bf1c1a00eec323d6e21ff7b9b12699afe04
Triggering test file: test/test_utils.py
```

源码目录：

```text
D:\Git\My_Git_Project\Bugs_2nd_try\BugsInPy_Workdir\case_002_bug11\youtube-dl
```

## 6.2 Bug 11 的源码问题

错误版本代码：

```python
def str_to_int(int_str):
    if int_str is None:
        return None
    int_str = re.sub(r'[,\.\+]', '', int_str)
    return int(int_str)
```

BugsInPy 补丁：

```diff
- if int_str is None:
-     return None
+ if not isinstance(int_str, compat_str):
+     return int_str
```

非字符串输入会被直接传给 `re.sub`。例如 `str_to_int(123)` 会触发：

```text
TypeError: expected string or bytes-like object, got 'int'
```

正确行为应为：

```python
str_to_int(123) == 123
```

## 6.3 BugsInPy 原始测试

```bash
python -m unittest -q test.test_utils.TestUtil.test_str_to_int
```

实际结果：

```text
Ran 1 test in 0.000s
OK
```

返回码：

```text
0
```

原因：历史测试只覆盖字符串输入，没有覆盖整数输入。

## 6.4 最小复现命令

```bash
python -c "from youtube_dl.utils import str_to_int; print(str_to_int(123))"
```

实际结果：

```text
TypeError: expected string or bytes-like object, got 'int'
```

返回码：

```text
1
```

## 6.5 SciCodePilot diagnosis

```text
External command return code: 1
Raw error type: TypeError
SciCodePilot error type: unsupported_external_failure
Traceback captured: yes
Isolated workspace created: yes
FailureMemory generated: yes
FailureMemory specialized: no
Original repo modified: no
```

## 6.6 SciCodePilot repair-plan

```text
Plan type: no_op
Valid PatchPlan generated: no
Patch applied: false
After return code: not available
```

## 6.7 最终状态

```text
final_status = unsupported_external_failure
```

---

# 7. 两个 case 的对比

| Case | Raw Error | Before RC | SciCodePilot Type | FailureMemory | Repair Plan | Patch |
|---|---|---:|---|---|---|---|
| Bug 17 | AssertionError | 1 | unsupported_external_failure | generic | no_op | not applied |
| Bug 11 | TypeError | 1 | unsupported_external_failure | generic | no_op | not applied |

---

# 8. 已验证可用的后端能力

SciCodePilot external smoke 当前已经能够：

1. 接收本地外部仓库路径；
2. 复制仓库到 isolated workspace；
3. 在 workspace 中执行指定命令；
4. 捕获 stdout、stderr 和 traceback；
5. 获取外部命令 return code；
6. 输出 `summary.md` 和 `summary.json`；
7. 生成通用 FailureMemory；
8. 保证原始仓库不被修改。

---

# 9. 当前后端瓶颈

1. external parser 尚未专门支持 `AssertionError`；
2. external parser 尚未专门支持 `TypeError`；
3. 已捕获真实异常文本，但仍统一归类为 `unsupported_external_failure`；
4. FailureMemory 只能生成通用兜底内容；
5. repair-plan 只能生成 `no_op`；
6. 无法生成 source-level PatchPlan；
7. 无法进入 patch apply；
8. 无法运行 after verification；
9. 尚未形成 `before failed → patched → passed` 完整闭环。

---

# 10. 对后端的建议

## 10.1 增加外部异常 parser

优先支持：

```text
AssertionError
TypeError
ValueError
KeyError
ImportError
```

## 10.2 提取结构化 traceback 信息

建议至少记录：

```text
exception type
exception message
source file
line number
function name
failing expression
command
workspace path
```

## 10.3 生成 specialized FailureMemory

Bug 17：

```text
Missing config key causes params.get(...) to return None,
then bool assertion fails.
```

Bug 11：

```text
Non-string input is passed to re.sub,
causing a type mismatch.
```

## 10.4 支持有效 PatchPlan 与 apply + verify

目标流程：

```text
copy workspace
→ apply patch
→ rerun original failing command
→ after_return_code = 0
→ confirm original repo unchanged
```

---

# 11. 当前可交付文件

建议后端优先查看：

```text
external_experiments/logs/
external_experiments/summaries/
external_experiments/scicodepilot_outputs/case_001_diagnosis/summary.md
external_experiments/scicodepilot_outputs/case_001_diagnosis/summary.json
external_experiments/scicodepilot_outputs/case_001_repair_plan/summary.md
external_experiments/scicodepilot_outputs/case_001_repair_plan/summary.json
external_experiments/scicodepilot_outputs/case_002_diagnosis/summary.md
external_experiments/scicodepilot_outputs/case_002_diagnosis/summary.json
external_experiments/scicodepilot_outputs/case_002_repair_plan/summary.md
external_experiments/scicodepilot_outputs/case_002_repair_plan/summary.json
external_experiments/external_all_attempts.csv
```

完整 workspace 目录体积较大，通常不必发送。

---

# 12. 阶段性结论

两个外部 case 均已证明：

```text
真实外部异常可以被执行、捕获和记录，
isolated workspace 正常，
但普通 Python 异常仍缺少 specialized parser，
FailureMemory 和 repair-plan 均未打通到有效修复层。
```

最终状态：

```text
Bug 17 → unsupported_external_failure
Bug 11 → unsupported_external_failure
```

下一步继续进行：

```text
case_003 / youtube-dl Bug 29
```
