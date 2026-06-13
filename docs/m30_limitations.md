# M30 实验局限性（Limitations）与解析器改进建议

## 1. 局限性：基于断言的外部测试失败尚未被细分类

在 M30 阶段的 BugsInPy External Pilot 实验中，SciCodePilot 已能够成功执行真实外部仓库测试，并捕获 unittest / AssertionError 类型失败。

但是这些失败目前会被统一分类为：

```text
unsupported_external_failure
```

而不是更具体的失败类别，例如：

```text
assertion_failure
unittest_failure
pytest_failure
external_test_failure
```

------

## 2. 发现该问题的实验案例

在以下实验中均观察到了该现象：

| 案例                       | 实际失败类型                      | 当前分类结果                 |
| -------------------------- | --------------------------------- | ---------------------------- |
| BugsInPy youtube-dl bug2   | AssertionError / unittest failure | unsupported_external_failure |
| Local Assertion Smoke Case | AssertionError                    | unsupported_external_failure |

实验结果表明：

- External Smoke Interface 已成功捕获失败；
- stderr、traceback、summary 文件均已生成；
- 失败证据能够被保存；
- 但当前解析器无法进一步识别 AssertionError 类型测试失败。

------

## 3. 为什么这是一个问题

大量真实 Python Benchmark（如 BugsInPy、pytest、unittest）中的缺陷并不会表现为：

```text
ImportError
ModuleNotFoundError
RuntimeError
```

而是表现为：

```text
FAILED (failures=1)
AssertionError
AssertionError: Expect 7 formats, got 6
```

当前系统虽然能够捕获这些失败信息，但无法区分：

```text
测试失败（Test Failure）
```

和

```text
未知外部失败（Unsupported External Failure）
```

因此会降低 Failure Taxonomy 的准确性。

------

## 4. 当前系统边界（Boundary）

因此 M30 阶段应当准确描述为：

```text
SciCodePilot External Smoke 已能够执行真实外部测试并捕获 AssertionError 失败证据，但目前仍将其分类为 unsupported_external_failure。
```

而不应描述为：

```text
SciCodePilot 已完全支持 BugsInPy Failure Taxonomy。
```

或：

```text
SciCodePilot 已完全理解 unittest / pytest 失败类型。
```

------

## 5. 后续改进方向

建议扩展 External Failure Parser（如 TracebackParser 或 FailureMemoryBuilder），增加以下失败类别：

```text
assertion_failure
unittest_failure
pytest_failure
external_test_failure
```

最简单的改进方式是增加规则匹配：

```text
AssertionError
FAILED (failures=1)
FAILED
pytest failure
unittest failure
```

当检测到上述模式时，将其分类为：

```text
external_test_failure
```

而不是：

```text
unsupported_external_failure
```

------

## 6. 对 M30 实验结论的影响

该问题不会影响 M30 External Pilot 的有效性。

相反，它提供了一项有价值的实验发现：

```text
SciCodePilot 已能够运行真实外部仓库测试并捕获失败证据，
但当前 Failure Parser 对 Assertion-Based Test Failure 的支持仍不完善，
未来需要增加更细粒度的 Failure Taxonomy。
```

该发现为后续改进：

- TracebackParser
- FailureMemoryBuilder
- External Smoke Failure Taxonomy

提供了明确方向。
