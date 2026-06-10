# M30 External Failure Taxonomy

| Case                  | Source            | Failure Observed                  | Current Classification       | Root Cause                                            | Suggested Fix                                                |
| --------------------- | ----------------- | --------------------------------- | ---------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| youtube-dl bug2       | BugsInPy          | AssertionError / unittest failure | unsupported_external_failure | Assertion-based test failure not recognized by parser | Add assertion_failure or external_test_failure classification |
| youtube-dl bug1       | BugsInPy          | Repository checkout failure       | setup_failure                | GitHub network connectivity issue                     | Record as environment/setup limitation                       |
| youtube-dl bug3       | BugsInPy          | Repository checkout failure       | setup_failure                | GitHub network connectivity issue                     | Record as environment/setup limitation                       |
| youtube-dl bug4       | BugsInPy          | Repository checkout failure       | setup_failure                | GitHub network connectivity issue                     | Record as environment/setup limitation                       |
| local assertion smoke | Local Python repo | AssertionError                    | unsupported_external_failure | Assertion failure captured but not categorized        | Extend TracebackParser for assertion failures                |

# M30 外部失败类型分析表

| 案例                  | 来源             | 观察到的失败现象                   | 当前系统分类                 | 根本原因                                        | 建议改进                                                     |
| --------------------- | ---------------- | ---------------------------------- | ---------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| youtube-dl bug2       | BugsInPy         | AssertionError / unittest 测试失败 | unsupported_external_failure | 当前外部失败解析器没有识别基于断言的测试失败    | 增加 assertion_failure 或 external_test_failure 分类         |
| youtube-dl bug1       | BugsInPy         | 仓库 checkout 失败                 | setup_failure                | GitHub 网络连接不稳定，导致真实仓库无法完整克隆 | 记录为环境 / setup 限制，不作为系统修复失败                  |
| youtube-dl bug3       | BugsInPy         | 仓库 checkout 失败                 | setup_failure                | GitHub 网络连接不稳定，导致真实仓库无法完整克隆 | 记录为环境 / setup 限制，不作为系统修复失败                  |
| youtube-dl bug4       | BugsInPy         | 仓库 checkout 失败                 | setup_failure                | GitHub 网络连接不稳定，导致真实仓库无法完整克隆 | 记录为环境 / setup 限制，不作为系统修复失败                  |
| local assertion smoke | 本地 Python repo | AssertionError                     | unsupported_external_failure | 系统能够捕获断言失败，但暂时没有进一步细分类    | 扩展 TracebackParser，使其支持 assertion_failure / unittest_failure |