# Open-Source Agent Positioning

## 1.背景

M30 阶段新增了：

- BugsInPy External Pilot
- Real LLM Smoke Test
- mini-swe-agent One-Case Attempt

因此需要说明 SciCodePilot 与现有开源 Agent 的定位差异。

需要注意的是：

- 本项目实际运行了 SciCodePilot 和 mini-swe-agent；
- 未实际运行 SWE-agent；
- 未实际运行 OpenHands。

因此本文件仅描述定位关系，不进行未经实验验证的性能比较。

------

## 2.M30 实际运行工具

| 工具           | 是否实际运行 | 实验内容                                                |
| -------------- | ------------ | ------------------------------------------------------- |
| SciCodePilot   | 是           | BugsInPy External Pilot、External Smoke、Real LLM Smoke |
| mini-swe-agent | 是           | Local Assertion Failure One-Case Attempt                |
| SWE-agent      | 否           | 未进行实验                                              |
| OpenHands      | 否           | 未进行实验                                              |

------

## 3.SciCodePilot 定位

SciCodePilot 当前主要关注：

- Diagnosis（问题诊断）
- Patch Planning（修复规划）
- Failure Memory
- Environment Diagnosis
- Reproducibility Tracking

M30 实验中：

- 成功运行 BugsInPy youtube-dl bug；
- 成功运行 External Smoke；
- 成功完成 10 个 Internal Tasks 的 Real LLM Smoke；
- 成功保存 Prompt、Response、Summary 等实验产物。

因此当前定位更接近：

```text
Research-Oriented Diagnostic and Repair Planning Platform
```

即：

```text
面向研究与实验验证的诊断和修复规划平台
```

------

## 4.mini-swe-agent 定位

M30 One-Case Attempt 中：

- 成功读取本地仓库；
- 成功复现 AssertionError；
- 自动修改 test_case.py；
- 自动重新运行测试；
- 成功完成修复验证。

因此其定位更接近：

```text
Autonomous Software Engineering Agent
```

即：

```text
具有自主执行和自动修复能力的软件工程 Agent
```

------

## 5.定位对比

| 维度              | SciCodePilot               | mini-swe-agent    |
| ----------------- | -------------------------- | ----------------- |
| 主要目标          | Diagnosis + Patch Planning | Autonomous Repair |
| Failure Memory    | 支持                       | 未观察到          |
| Structured Output | 支持                       | 不保证            |
| External Smoke    | 支持                       | 不适用            |
| 自动修改代码      | 否（默认）                 | 是                |
| 自动验证修复      | 有限                       | 支持              |
| 实验记录保存      | summary.md / summary.json  | trajectory.json   |
| 安全边界          | 强                         | 相对较弱          |
| 自主性            | 中                         | 高                |

------

## 6.M30 阶段结论

根据实际完成的实验：

- mini-swe-agent 展现出了较强的自动修复能力；
- SciCodePilot 展现出了较强的结构化诊断与实验记录能力；
- 两者关注点不同；

因此：

```text
mini-swe-agent 更强调自动执行与自动修复；

SciCodePilot 更强调结构化诊断、Failure Memory、可复现性与实验分析。
```

M30 的目标并不是证明 SciCodePilot 全面优于开源 Agent，而是通过真实 External Pilot、Real LLM Smoke 和 One-Case Attempt 说明：

```text
SciCodePilot 在诊断、修复规划和实验可复现性方面具有明确定位。
```