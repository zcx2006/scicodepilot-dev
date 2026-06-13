# Open-Source Agent One-Case Comparison

## 实验背景

本实验选择同一个本地 AssertionError 案例：

```text
AssertionError: Expect 7 formats, got 6
```

分别使用：

- SciCodePilot External Smoke
- mini-swe-agent 2.3.1 + DeepSeek Chat

进行测试，并记录其行为差异。

------

## 实验案例

| 项目     | 内容                                     |
| -------- | ---------------------------------------- |
| 测试目录 | `LocalSmokeCases/case_assertion_failure` |
| 失败命令 | `python test_case.py`                    |
| 错误类型 | AssertionError                           |
| 错误信息 | Expect 7 formats, got 6                  |

------

## 实验结果对比

| 对比项              | SciCodePilot                         | mini-swe-agent        |
| ------------------- | ------------------------------------ | --------------------- |
| 测试案例            | Local Assertion Smoke                | Local Assertion Smoke |
| 错误复现            | 成功                                 | 成功                  |
| AssertionError 捕获 | 成功                                 | 成功                  |
| 自动分析根因        | 成功                                 | 成功                  |
| 自动生成修复建议    | PatchPlan / Diagnosis                | 自动生成并执行 Patch  |
| 自动修改文件        | 否                                   | 是                    |
| 自动验证修复结果    | 否（当前 External Smoke 以诊断为主） | 是                    |
| 测试验证命令        | 用户执行                             | Agent 自动执行        |
| 最终测试通过        | 未自动验证                           | 成功通过              |
| 输出文件            | summary.md / summary.json            | trajectory.json       |
| Failure Memory      | 支持                                 | 不支持                |
| Structured Output   | 支持                                 | 不保证                |
| Safety Boundary     | 强                                   | 相对较弱              |
| 自主修复能力        | 中                                   | 高                    |

------

## mini-swe-agent 实际行为

mini-swe-agent 自动完成了以下步骤：

1. 查看目标目录；
2. 读取 `test_case.py`；
3. 运行 `python test_case.py`；
4. 发现 AssertionError；
5. 自动修改：

原始代码：

```python
return [1, 2, 3, 4, 5, 6]
```

修改为：

```python
return [1, 2, 3, 4, 5, 6, 7]
```

1. 再次运行：

```bash
python test_case.py
```

1. 返回码：

```text
returncode = 0
```

完成修复验证。

------

## SciCodePilot 实际行为

SciCodePilot External Smoke：

1. 成功运行失败测试；
2. 捕获 AssertionError；
3. 生成 summary.md；
4. 生成 summary.json；
5. 保存 Failure Evidence；
6. 保存 Failure Memory；

但当前版本：

```text
AssertionError
```

仍被归类为：

```text
unsupported_external_failure
```

因此 M30 中新增了：

- Failure Taxonomy
- Limitation Analysis

用于说明该问题。

------

## 优势与不足分析

### SciCodePilot 优势

- Structured Patch Planning
- Failure Memory
- Environment Diagnosis
- Reproducibility Tracking
- Safety Boundary
- Structured Summary Output

### SciCodePilot 不足

- 自动修复能力有限
- AssertionError 分类仍需细化
- 当前以诊断为主

### mini-swe-agent 优势

- 自动修复能力强
- 自动验证修复结果
- Agent 自主性高
- 可直接修改代码

### mini-swe-agent 不足

- Token 消耗更高
- 容易进入长循环
- 输出结构化程度较低
- 缺少 Failure Memory 机制
- 会直接修改工作目录文件

------

## M30 结论

本次 One-Case Attempt 表明：

- mini-swe-agent 在简单本地缺陷上具有更强的自动修复能力；
- SciCodePilot 更强调结构化诊断、Failure Memory、可复现性和安全边界；
- 两者定位不同，不应仅以是否自动修复成功作为唯一评价标准。

因此：

```text
mini-swe-agent 更接近 Autonomous Software Engineering Agent；

SciCodePilot 更接近 Research-Oriented Diagnostic and Repair Planning Platform。
```
