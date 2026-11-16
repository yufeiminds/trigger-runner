# trigger-runner

一个用于衡量 agent skill 是否在正确的请求上触发的小型测试工具。对于某个
skill 的 `evals/eval_queries.json` 中的每个 `(query, should_trigger)` 二元组，
它会向正在运行自定义 DeepSeek 模型的 OpenCode 发起请求，并记录该 skill 是否
真的被调用。

## 快速开始

需要 Python 3.9+（仅使用标准库）、`PATH` 中可用的
[`opencode`](https://opencode.ai)、环境变量 `DEEPSEEK_API_KEY`，以及一个包含
`skills/<name>/evals/eval_queries.json` 的 skill 仓库。

1. 导出 API key：

   ```shell
   export DEEPSEEK_API_KEY=...
   ```

2. 设置 `trigger_runner.py` 顶部的 `ROOT`、`EVAL_DIR` 和 `SKILLS`。
   `ROOT` 是 skill 仓库；`EVAL_DIR` 存放 `opencode.json`，并且其
   `.opencode/skills/` 下必须包含相同的 skill。

3. 运行：

   ```shell
   python3 trigger_runner.py
   ```

你会看到每个用例一行输出，以及每个 skill 的通过计数：

```text
[1/32] clean-code PASS expected=True got=True other=[] 12.4s
[2/32] clean-code FAIL expected=False got=True other=[] 9.8s
...
clean-code: 29/32
diataxis: 30/32
```

完整结果写入 `/tmp/trigger-results.json`。如果会话可能超过超时时间，改用
`trigger_runner2.py`：它会保留部分输出，并输出原始触发计数而非通过/失败。

完整步骤见
[docs/tutorials/run-your-first-evaluation.md](docs/tutorials/run-your-first-evaluation.md)
（英文）。

## 评估内容

每个同时参与评估的 skill 提供一个 JSON 数组：

```json
[
  { "query": "Break up this 1200-line handler file.", "should_trigger": true },
  { "query": "What time is it in Tokyo?", "should_trigger": false }
]
```

当该 skill 的实际触发状态与 `should_trigger` 一致时，用例通过：正例必须调用
skill，负例必须不调用。调用情况从 OpenCode 的 JSON 事件流中检测。

## 文档

| 文档                                                          | 内容                                     |
| ------------------------------------------------------------- | ---------------------------------------- |
| [教程](docs/tutorials/run-your-first-evaluation.md)           | 从干净检出到完成一次触发评估（英文）     |
| [配置](docs/reference/configuration.md)                       | 模块常量与 `opencode.json`（英文）       |
| [trigger_runner](docs/reference/trigger-runner.md)            | `run_query()`、`main()` 与命令行（英文） |
| [trigger_runner2](docs/reference/second-pass-runner.md)       | 容忍超时的第二遍评估，含 `TIMEOUT`（英文） |
| [结果](docs/reference/results.md)                             | 控制台输出、JSON 字段与通过规则（英文）  |

## 仓库结构

| 路径                 | 用途                                                       |
| -------------------- | ---------------------------------------------------------- |
| `trigger_runner.py`  | 主 runner：逐用例输出 PASS/FAIL，并统计每个 skill 的通过率   |
| `trigger_runner2.py` | 容忍超时的变体：保留部分输出，并输出原始触发计数             |
| `skill-eval/`        | 作为 `EVAL_DIR` 的 OpenCode 工作区；存放 provider 配置和已安装的 skill |
| `docs/`              | 教程与参考文档                                             |
| `README.zh.md`       | 本文档的中文版本                                           |
| `anthropics-skills/`、`skilltest/`、`skillinit/` | 开发 skill 时使用的本地 skill 检出和临时工作区 |

## 局限性

- 每个查询只运行一次，因此结果中包含模型和采样噪声；在把单次失败当作回归之前
  请先重跑。
- 路径、模型、超时和 skill 列表都是硬编码的——这是一个一次性测试工具，而非
  可配置的 CLI。
- 它只衡量触发情况。输出质量存放在 `evals/evals.json` 中。
- Provider 错误和超时可能看起来像未触发。在下结论前请检查 `error` 和
  `timed_out` 字段。
- 每个用例都是一次付费模型会话；对多个 skill 做完整评估会消耗真实的时间和 token。
