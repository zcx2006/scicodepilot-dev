# SciCodePilot 新增 BugsInPy Case 004–007 后端交接文档

## 1. 交接目的

本文档用于向 SciCodePilot 后端负责人交接本轮新增的 4 个真实 BugsInPy `youtube-dl` case 测试结果：

- `case_004`：youtube-dl Bug 28
- `case_005`：youtube-dl Bug 3
- `case_006`：youtube-dl Bug 13
- `case_007`：youtube-dl Bug 21

本轮使用的 SciCodePilot 代码主要针对先前 `case_001–003` 做过专门更新，因此本轮重点不是证明修复成功，而是检查：

```text
新 Bug 能否稳定复现
→ SciCodePilot 能否识别真实失败类型
→ FailureMemory 是否与真实根因一致
→ 是否能生成可执行 PatchPlan
→ 是否能在 isolated workspace 中应用补丁
→ 是否能进行 after verification
```

修复成功仍严格按以下条件判定：

```text
before_return_code != 0
patch_applied == true
after_return_code == 0
original_repo_mutated == false
```

本轮 4 个 case 均未达到 `patch_success`。

---

## 2. 测试环境与目录

### 2.1 根目录

```text
D:\Git\My_Git_Project\BugsInPy_0616_2
```

### 2.2 主要目录

```text
D:\Git\My_Git_Project\BugsInPy_0616_2
├─BugsInPy
├─scicodepilot-dev-main
├─BugsInPy_Workdir
│  ├─archives
│  ├─case_004_bug28
│  ├─case_005_bug3
│  ├─case_006_bug13
│  └─case_007_bug21
├─external_experiments_0616_2
└─scripts_0616_2
```

### 2.3 源码获取方式

4 个 case 均使用 GitHub exact buggy commit ZIP 获取源码，而不是标准 `bugsinpy-checkout` 完整 clone。

应如实记录为：

```text
Source acquisition: GitHub exact commit ZIP archive
Exact buggy commit: yes
Standard BugsInPy checkout: not used for final source preparation
Git metadata available: no
```

### 2.4 Python 与运行方式

- youtube-dl 复现命令统一使用 `py -3.11`。
- SciCodePilot 使用：

```text
scripts/run_external_repo_smoke.py
```

- 使用的模式：

```text
diagnosis
repair-plan
repair --confirm-apply
```

- 所有 repair 均启用：

```text
--copy-workspace
```

- 4 个 case 最终都确认：

```text
original_repo_mutated = false
```

---

## 3. 总体结果

| Case | Bug | Buggy commit | Official test RC | Repro RC | Raw error | SciCodePilot type | Specialized memory | PatchPlan | Patch applied | After RC | Final status |
|---|---:|---|---:|---:|---|---|---|---|---|---|---|
| case_004 | 28 | `bd1512d19649c280197729814766d590ea6c023b` | 0 | 1 | ValueError | `unsupported_external_failure` | false | false | false | null | `unsupported_external_failure` |
| case_005 | 3 | `f5469da9e6e259c1690c7ef54f1da1c19f65036f` | 0 | 1 | AssertionError | `external_assertion_failure` | true，但根因错误 | false | false | null | `patch_failed` |
| case_006 | 13 | `6945b9e78f38284eb4e440b7badea2fc60b66c2f` | 0 | 1 | AssertionError | `external_assertion_failure` | true，但根因错误 | false | false | null | `patch_failed` |
| case_007 | 21 | `96182695e4e37795a30ab143129c91dab18a9865` | 0 | 1 | AssertionError | `external_assertion_failure` | true，但根因错误 | false | false | null | `patch_failed` |

统计：

```text
新增 case 数：4
buggy commit ZIP 下载并解压成功：4
官方历史测试可运行：4
官方历史测试返回 0 / 未覆盖目标缺陷：4
最小复现成功（before_return_code = 1）：4
unsupported_external_failure：1
external_assertion_failure：3
正确根因诊断：0
有效 PatchPlan：0
patch applied：0
after verification：0
patch_success：0
原仓库保持未修改：4
```

---

# 4. Case 004：youtube-dl Bug 28

## 4.1 基本信息

```text
Case ID: case_004
Project: youtube-dl
Bug ID: 28
Buggy commit: bd1512d19649c280197729814766d590ea6c023b
Fixed revision: 7aefc49c4013efb5056b2c1237e22c52cb5d3c49
Triggering test file: test/test_utils.py
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\BugsInPy_Workdir\case_004_bug28\youtube-dl
```

## 4.2 官方历史测试

```bash
py -3.11 -m unittest -q test.test_utils.TestUtil.test_unescape_html
```

结果：

```text
Ran 1 test
OK
return code = 0
```

说明历史测试未覆盖本次缺陷输入。

## 4.3 最小复现

复现脚本：

```text
repro_bug28.py
```

复现命令：

```bash
py -3.11 repro_bug28.py
```

核心输入：

```python
unescapeHTML('&#x110000;')
```

`0x110000` 超出合法 Unicode 码点范围。

实际失败：

```text
ValueError: chr() arg not in range(0x110000)
before_return_code = 1
```

目标行为：

```text
无效数字 HTML entity 不应导致程序崩溃；
应保留原始 entity 字符串。
```

## 4.4 SciCodePilot 结果

```text
detected_failure_type = unsupported_external_failure
failure_memory_generated = true
failure_memory_specialized = false
patch_plan_generated = false
patch_applied = false
after_return_code = null
original_repo_mutated = false
final_status = unsupported_external_failure
```

RepairPlan：

```text
plan_type = no_op
```

## 4.5 后端问题

当前 parser 没有将该 traceback 中的 `ValueError` 解析为结构化外部错误，未提取：

```text
exception_type = ValueError
file_path = youtube_dl/utils.py
function = _htmlentity_transform
failing expression = compat_chr(int(numstr, base))
```

因此 FailureMemory 只能给出通用兜底说明，后续 PatchPlan 无法生成。

## 4.6 官方修复方向（仅用于根因核验）

应在数字实体转换处处理 `compat_chr(...)` 可能抛出的 `ValueError`，并保留原始实体。

后端实现时不建议 hard-code Bug ID 或固定输入 `&#x110000;`，应泛化为：

```text
数字 HTML entity
→ int 转换成功
→ Unicode code point 非法
→ 捕获 ValueError
→ 保留原始 entity
```

---

# 5. Case 005：youtube-dl Bug 3

## 5.1 基本信息

```text
Case ID: case_005
Project: youtube-dl
Bug ID: 3
Buggy commit: f5469da9e6e259c1690c7ef54f1da1c19f65036f
Fixed revision: 95f3f7c20a05e7ac490e768b8470b20538ef8581
Triggering test file: test/test_utils.py
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\BugsInPy_Workdir\case_005_bug3\youtube-dl
```

## 5.2 官方历史测试

```bash
py -3.11 -m unittest -q test.test_utils.TestUtil.test_unescape_html
```

结果：

```text
Ran 1 test
OK
return code = 0
```

## 5.3 最小复现

复现脚本：

```text
repro_bug3.py
```

核心输入：

```python
source = '&a&quot;'
expected = '&a"'
actual = '&a&quot;'
```

实际失败：

```text
AssertionError:
Malformed HTML entity was decoded incorrectly:
expected '&a"', got '&a&quot;'

before_return_code = 1
```

真实问题是 HTML entity 的正则匹配范围过宽，允许匹配跨越前一个 `&`。

## 5.4 SciCodePilot 结果

```text
detected_failure_type = external_assertion_failure
failure_memory_generated = true
failure_memory_specialized = true
patch_plan_generated = false
patch_applied = false
after_return_code = null
original_repo_mutated = false
final_status = patch_failed
```

## 5.5 FailureMemory 错误

虽然标记为：

```text
failure_memory_specialized = true
```

但生成的根因是假设：

```text
dict.get(...) 返回 None
随后进入 bool assertion
配置 key 缺失
```

这与 HTML entity 解析完全无关，明显复用了 case_001 的专用模板。

因此本 case 应评价为：

```text
错误类型粗粒度识别成功
FailureMemory specialized 标记形式上成功
真实根因诊断失败
PatchPlan 未生成
自动修复失败
```

## 5.6 官方修复方向（仅用于根因核验）

HTML entity 匹配不应跨越另一个 `&`。修复方向是收紧 entity 正则字符集合，使其在遇到 `&` 时停止。

后端不应 hard-code `&a&quot;`，应泛化识别：

```text
字符串解码断言失败
→ actual 保留了后续合法 entity
→ 定位 unescapeHTML 的 entity regex
→ 修正 entity token 边界
```

---

# 6. Case 006：youtube-dl Bug 13

## 6.1 基本信息

```text
Case ID: case_006
Project: youtube-dl
Bug ID: 13
Buggy commit: 6945b9e78f38284eb4e440b7badea2fc60b66c2f
Fixed revision: fad4ceb53404227f471af2f3544c4c14a5df4acb
Triggering test file: test/test_utils.py
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\BugsInPy_Workdir\case_006_bug13\youtube-dl
```

## 6.2 官方历史测试

```bash
py -3.11 -m unittest -q test.test_utils.TestUtil.test_urljoin
```

结果：

```text
Ran 1 test
OK
return code = 0
```

## 6.3 最小复现

复现脚本：

```text
repro_bug13.py
```

核心输入：

```python
base = None
path = 'rtmp://media.example.com/live/stream'
```

期望：

```text
'rtmp://media.example.com/live/stream'
```

实际：

```text
None
```

失败：

```text
AssertionError:
Absolute URL with a non-HTTP scheme was handled incorrectly

before_return_code = 1
```

真实问题：旧实现只识别 `http://`、`https://` 和 `//`，没有把其他合法 scheme 的 URL 视为绝对 URL。

## 6.4 SciCodePilot 结果

```text
detected_failure_type = external_assertion_failure
failure_memory_generated = true
failure_memory_specialized = true
patch_plan_generated = false
patch_applied = false
after_return_code = null
original_repo_mutated = false
final_status = patch_failed
```

## 6.5 FailureMemory 错误

生成的根因仍是：

```text
dict.get(...) 返回 None
bool assertion
缺失配置项
```

与 `urljoin` 的协议识别问题无关。

这说明当前 `external_assertion_failure` 的 specialized FailureMemory 不是通用断言分析，而是对 case_001 模式的过拟合。

## 6.6 官方修复方向（仅用于根因核验）

应将绝对 URL scheme 识别从仅支持 HTTP(S) 扩展为合法 URI scheme，例如：

```text
字母开头
后续允许字母、数字、+、-、.
然后是 ://
```

后端不应 hard-code `rtmp`，应泛化为 URI scheme 规则。

---

# 7. Case 007：youtube-dl Bug 21

## 7.1 基本信息

```text
Case ID: case_007
Project: youtube-dl
Bug ID: 21
Buggy commit: 96182695e4e37795a30ab143129c91dab18a9865
Fixed revision: 4b5de77bdb7765df4797bf068592926285ba709a
Triggering test file: test/test_utils.py
```

源码目录：

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\BugsInPy_Workdir\case_007_bug21\youtube-dl
```

## 7.2 官方历史测试

```bash
py -3.11 -m unittest -q test.test_utils.TestUtil.test_urljoin
```

结果：

```text
Ran 1 test
OK
return code = 0
```

## 7.3 最小复现

复现脚本：

```text
repro_bug21.py
```

测试 3 种输入：

```text
1. str base + bytes path
2. bytes base + str path
3. bytes base + bytes path
```

三个 case 的实际结果均为：

```text
None
```

期望均为：

```text
https://example.com/root/video/page.html
```

失败：

```text
AssertionError: Bytes URL handling failed
before_return_code = 1
```

真实问题：旧实现没有在类型检查前将 `bytes` 类型的 `base` 和 `path` 解码为 UTF-8 字符串。

## 7.4 SciCodePilot 结果

```text
detected_failure_type = external_assertion_failure
failure_memory_generated = true
failure_memory_specialized = true
patch_plan_generated = false
patch_applied = false
after_return_code = null
original_repo_mutated = false
final_status = patch_failed
```

## 7.5 FailureMemory 错误

仍错误指向：

```text
dict.get(...)
None
bool assertion
配置 key 缺失
```

与 bytes URL 解码无关。

## 7.6 执行过程中的无效运行

本 case 出现过两次无效运行：

```text
1. 包装脚本漏传 CASE_NAME，outer return code = 2
2. diagnosis 阶段被 Ctrl+C 中断，outer return code = 130
```

以上运行均不计入最终结果。

最终通过分步直接执行：

```text
diagnosis
repair-plan
repair
```

成功生成最终 `repair/summary.md` 和 `repair/summary.json`。最终有效状态为：

```text
patch_failed
```

## 7.7 官方修复方向（仅用于根因核验）

在 `urljoin` 进行字符串类型检查之前：

```text
bytes path → decode('utf-8')
bytes base → decode('utf-8')
```

后端不应 hard-code当前三个输入组合，应泛化为：

```text
函数期望字符串
→ traceback / assertion 显示 bytes 输入导致 None
→ 检查函数入口处类型守卫
→ 在类型判断前执行安全 UTF-8 decode
```

---

# 8. 本轮暴露的后端核心问题

## 8.1 AssertionError parser 只完成了错误类型识别

3 个 AssertionError case 均被识别为：

```text
external_assertion_failure
```

这说明粗粒度 parser 已生效。

但其后生成的 FailureMemory 全部套用了 case_001 的固定根因：

```text
dict.get(None)
→ bool assertion
→ 缺失配置 key
```

真实缺陷分别为：

```text
Bug 3：HTML entity token 边界
Bug 13：非 HTTP URI scheme 识别
Bug 21：bytes URL 输入解码
```

结论：

> 当前 specialized FailureMemory 对 AssertionError 存在明显 case-specific overfitting，尚未形成通用的 assertion evidence extraction 和根因推断能力。

## 8.2 ValueError parser 缺失

Bug 28 的 traceback 已明确给出：

```text
ValueError: chr() arg not in range(0x110000)
youtube_dl/utils.py
_htmlentity_transform
compat_chr(...)
```

但系统仍输出：

```text
unsupported_external_failure
```

建议新增：

```text
external_value_error
```

并提取：

```text
exception type
source file
line number
function
failing expression
error message
```

## 8.3 Patch planner 仍是 case-specific

4 个 case 均未生成有效 PatchPlan：

```text
patch_plan_generated = false
plan_type = no_op
```

说明当前 planner 只覆盖 case_001–003 的已知模式，不能根据新的结构化证据生成局部修复。

## 8.4 specialized 标志语义不可靠

Case 005–007 均出现：

```text
failure_memory_specialized = true
```

但内容与真实 bug 完全无关。

建议 specialized 不只表示“走了某个专用分支”，还应增加：

```text
evidence grounding
target function consistency
root-cause confidence
matched repair pattern
```

否则该字段会夸大实际诊断能力。

## 8.5 wrapper 脚本可用性

Case 007 暴露两个运行层问题：

1. 参数不足时只输出 Usage，建议同时打印收到的参数数量和示例命令；
2. 所有输出重定向到日志时，终端看起来像“卡住”，容易误按 Ctrl+C。

建议 wrapper：

```text
每个 mode 开始时打印时间
每个 mode 完成时打印 return code
定期输出进度或明确提示“正在运行，请勿中断”
```

---

# 9. 推荐后端修改优先级

## P0：修正 AssertionError FailureMemory 的过拟合

不要仅根据：

```text
exception_type = AssertionError
```

直接套用 case_001 的配置项模板。

至少应结合：

```text
assertion message
actual / expected 值
repro script 中调用的目标函数
application traceback
目标源码附近代码
```

建议将 assertion 分成：

```text
bool/config assertion
return-value mismatch
string transformation mismatch
URL/path handling mismatch
type handling mismatch
```

## P0：新增 ValueError parser

新增 `external_value_error`，首先覆盖 traceback 中明确的：

```text
ValueError
file
line
function
failing expression
message
```

Bug 28 可作为回归测试。

## P1：让 PatchPlan 基于目标函数和源码上下文生成

当前 root cause 错误后，planner 只能 `no_op`。

建议：

```text
repro caller symbol
→ traceback target symbol
→ source window
→ actual/expected evidence
→ bounded local PatchPlan
```

并限制修改：

```text
单文件
单函数
小范围 diff
禁止修改 repro script
```

## P1：增加诊断质量检查

在进入 patch planner 前检查：

```text
FailureMemory 提到的函数是否出现在 traceback/source 中
FailureMemory 提到的变量是否真实存在
FailureMemory 是否解释 actual/expected 差异
```

例如本轮 `dict.get`、bool assertion 在 Bug 3、13、21 中均不存在，应自动降低置信度并拒绝标记为 specialized。

## P2：改善 CLI / wrapper 可观测性

增加：

```text
mode start/end timestamp
current case
current command
output directory
heartbeat / running message
interruption handling
```

---

# 10. 建议回归目标

后端更新后，建议按以下顺序回归：

## 第一优先：Case 007 / Bug 21

原因：

- 逻辑简单；
- 类型处理局部；
- 预期补丁小；
- 有 3 个输入组合，可检查泛化；
- 很适合作为“新 case 修复成功”展示。

目标：

```text
before = 1
diagnosis = bytes input handling
PatchPlan = decode bytes before str validation
patch_applied = true
after = 0
original_repo_mutated = false
final_status = patch_success
```

## 第二优先：Case 006 / Bug 13

用于检查 URI scheme 规则是否可以泛化，而不是 hard-code `rtmp`。

## 第三优先：Case 004 / Bug 28

用于检查新增 ValueError parser 和异常保护类修复。

## 第四优先：Case 005 / Bug 3

涉及 regex token 边界，推理难度略高，可作为 planner 泛化能力补充。

---

# 11. 建议发送给后端的文件

## 11.1 必发文件

### A. 本交接文档

```text
0616_backend_handoff_bugsinpy_cases004_007.md
```

### B. 4 个最小复现脚本

```text
BugsInPy_Workdir\case_004_bug28\youtube-dl\repro_bug28.py
BugsInPy_Workdir\case_005_bug3\youtube-dl\repro_bug3.py
BugsInPy_Workdir\case_006_bug13\youtube-dl\repro_bug13.py
BugsInPy_Workdir\case_007_bug21\youtube-dl\repro_bug21.py
```

### C. 每个 case 最终 repair 摘要

```text
external_experiments_0616_2\case_004_bug28\outputs\repair\summary.md
external_experiments_0616_2\case_004_bug28\outputs\repair\summary.json

external_experiments_0616_2\case_005_bug3\outputs\repair\summary.md
external_experiments_0616_2\case_005_bug3\outputs\repair\summary.json

external_experiments_0616_2\case_006_bug13\outputs\repair\summary.md
external_experiments_0616_2\case_006_bug13\outputs\repair\summary.json

external_experiments_0616_2\case_007_bug21\outputs\repair\summary.md
external_experiments_0616_2\case_007_bug21\outputs\repair\summary.json
```

### D. 官方测试与最小复现日志

每个 case 发送：

```text
logs\<bug>_info.log
logs\official_before.log 或 before.log
logs\official_before_return_code.txt 或 before_return_code.txt
logs\repro_before.log
logs\repro_before_return_code.txt
```

对应目录：

```text
external_experiments_0616_2\case_004_bug28\logs\
external_experiments_0616_2\case_005_bug3\logs\
external_experiments_0616_2\case_006_bug13\logs\
external_experiments_0616_2\case_007_bug21\logs\
```

> Case 004、005 的官方测试日志文件名可能是 `before.log`；Case 006、007 使用 `official_before.log`。打包前按本地实际文件名确认。

## 11.2 建议发送文件

### A. diagnosis 和 repair-plan 的 summary

每个 case 若存在，发送：

```text
outputs\diagnosis\summary.md
outputs\diagnosis\summary.json
outputs\repair-plan\summary.md
outputs\repair-plan\summary.json
```

这些文件能帮助后端对比三个 mode 的字段变化。

### B. 三阶段运行日志

```text
logs\diagnosis.log
logs\repair-plan.log
logs\repair.log
logs\diagnosis_script_return_code.txt
logs\repair-plan_script_return_code.txt
logs\repair_script_return_code.txt
```

### C. 可复现运行脚本

```text
scripts_0616_2\run_scicodepilot_case.sh
```

可选发送：

```text
env_0616_2.sh
```

该文件主要是本地路径配置，发送前确认不含密钥或敏感信息。

## 11.3 不建议发送

以下内容体积大或没有必要：

```text
outputs\*\workspace\
完整 youtube-dl 源码副本
BugsInPy_Workdir\archives\*.zip
Python 虚拟环境
__pycache__
.pyc
.git（本轮 ZIP 源码本身无 Git 元数据）
case_007 的 interrupted_run_130（除非后端需要排查 CLI 体验）
```

如果某个 case 的 diagnosis 或 repair-plan 独立 summary 不存在，至少发送：

```text
repro script
repro log
final repair summary.md
final repair summary.json
```

因为 repair summary 已包含 Diagnosis、FailureMemory、Repair Planning 和 Safety Boundary。

---

# 12. 给后端负责人的最终结论

```text
本轮新增完成 4 个 BugsInPy youtube-dl case：

- case_004 / Bug 28
- case_005 / Bug 3
- case_006 / Bug 13
- case_007 / Bug 21

4 个 buggy commit 均成功获取，官方历史测试均可运行但返回 0，
因此根据 BugsInPy 补丁分别编写了最小复现脚本。
4 个最小复现均稳定产生 before_return_code = 1。

SciCodePilot 结果：
- Bug 28 的 ValueError 被归为 unsupported_external_failure；
- Bug 3、13、21 被归为 external_assertion_failure；
- 但三个 AssertionError 的 FailureMemory 均错误复用了 case_001 的
  dict.get(None) / bool assertion 根因模板；
- 4 个 case 均未生成有效 PatchPlan；
- 均未应用补丁；
- 均未执行 after verification；
- 原始仓库均未被修改；
- 最终为 1 个 unsupported_external_failure、3 个 patch_failed、0 个 patch_success。

本轮最重要的后端结论不是 runner 失败，而是：
1. AssertionError specialized FailureMemory 存在 case-specific overfitting；
2. ValueError parser 尚未支持；
3. Patch planner 只能处理已适配的 case001–003 模式；
4. specialized=true 目前不能代表根因诊断正确。

建议优先回归 Case 007（bytes URL decode），然后依次处理
Case 006（通用 URI scheme）、Case 004（ValueError）和 Case 005（regex 边界）。
```
