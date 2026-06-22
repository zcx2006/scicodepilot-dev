# SciCodePilot BugsInPy Case 001–007 状态汇总

## 一、总体结果

| Case | Bug | Before RC | Failure Type | Specialized Memory | PatchPlan | Patch Applied | After RC | Original Repo Mutated | Final Status |
|---|---:|---:|---|---|---|---|---:|---|---|
| case_001 | 17 | 1 | `external_assertion_failure` | true | true | true | 0 | false | `patch_success` |
| case_002 | 11 | 1 | `external_type_error` | true | true | true | 0 | false | `patch_success` |
| case_003 | 29 | 1 | `external_assertion_failure` | true | true | true | 0 | false | `patch_success` |
| case_004 | 28 | 1 | `unsupported_external_failure` | false | false | false | null | false | `unsupported_external_failure` |
| case_005 | 3 | 1 | `external_assertion_failure` | true | false | false | null | false | `patch_failed` |
| case_006 | 13 | 1 | `external_assertion_failure` | true | false | false | null | false | `patch_failed` |
| case_007 | 21 | 1 | `external_assertion_failure` | true | false | false | null | false | `patch_failed` |

## 二、状态统计

- 总 Case 数：`7`
- `patch_success`：`3`
- `unsupported / unsupported_external_failure`：`1`
- `patch_failed`：`3`
- `env_failed`：`0`
- 缺少最终 summary：`0`

## 三、结果说明

### Case 001–003

这三个案例是后端更新后重点适配并进行回归验证的案例。
它们均满足：

```text
before_return_code != 0
patch_plan_generated = true
patch_applied = true
after_return_code = 0
original_repo_mutated = false
final_status = patch_success
```

### Case 004–007

这四个案例用于检测当前后端面对未专门适配错误时的泛化能力。

- Case 004 的 ValueError 未被当前 parser 支持；
- Case 005–007 虽识别为 AssertionError，但根因分析错误；
- 四个案例均未生成有效 PatchPlan；
- 四个原始仓库均未被修改。

## 四、原始 Summary 文件位置

### case_001 / Bug 17

```text
D:\Git\My_Git_Project\BugsInPy_0616\external_experiments_0616\branch_results\case001\outputs\bug17_repair\summary.json
```

### case_002 / Bug 11

```text
D:\Git\My_Git_Project\BugsInPy_0616\external_experiments_0616\branch_results\cases002_003\outputs\bug11_repair\summary.json
```

### case_003 / Bug 29

```text
D:\Git\My_Git_Project\BugsInPy_0616\external_experiments_0616\branch_results\cases002_003\outputs\bug29_repair\summary.json
```

### case_004 / Bug 28

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\external_experiments_0616_2\case_004_bug28\outputs\repair\summary.json
```

### case_005 / Bug 3

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\external_experiments_0616_2\case_005_bug3\outputs\repair\summary.json
```

### case_006 / Bug 13

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\external_experiments_0616_2\case_006_bug13\outputs\repair\summary.json
```

### case_007 / Bug 21

```text
D:\Git\My_Git_Project\BugsInPy_0616_2\external_experiments_0616_2\case_007_bug21\outputs\repair\summary.json
```

