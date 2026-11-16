# `trigger_runner` 模块

> 使用 OpenCode + 自定义 DeepSeek provider 的一次性触发评估 runner。

该模块通过 `opencode run` 运行每个查询，并检查 JSON 事件流中的 `skill` 工具调用，
来评估 agent skill 是否在正确的查询上被调用。

## 调用方式

```text
python3 trigger_runner.py
```

## `run_query(skill, item)`

运行一个 `(query, should_trigger)` 用例并返回一条结果记录。

该函数没有 docstring；此描述取自实现。

| 参数    | 类型   | 说明                                        |
| ------- | ------ | ------------------------------------------- |
| `skill` | `str`  | 要在事件流中查找的 skill 名称。             |
| `item`  | `dict` | 包含 `query` 和 `should_trigger` 键的用例。 |

该函数在 `EVAL_DIR` 中执行参数向量
`opencode run --format json --auto -m <MODEL> <query>`，超时时间为 150 秒。
标准输出的每一行都会按 JSON 解析。当某一行的 `part.type` 为 `"tool"` 且
`part.tool` 为 `"skill"` 时，该行贡献一次调用；调用的名称为
`part.state.input.name`。名称等于 `skill` 时会设置 `triggered`，而 `SKILLS`
中的任何其他名称会被加入 `others`。

非零退出会贡献一个形如 `exit <code>: <stderr 的前 200 个字符>` 的错误。
`TimeoutExpired` 异常会贡献错误 `"timeout"`。

返回值为 `dict`：

| 键               | 类型         | 说明                                            |
| ---------------- | ------------ | ----------------------------------------------- |
| `skill`          | `str`        | 被测 skill。                                    |
| `query`          | `str`        | 查询文本。                                      |
| `should_trigger` | `bool`       | 预期的触发状态。                                |
| `triggered`      | `bool`       | 该 skill 是否被调用。                           |
| `other_skill`    | `list[str]`  | 其他被调用且参与评估的 skill，已排序。          |
| `pass`           | `bool`       | `triggered == should_trigger`。                 |
| `seconds`        | `float`      | 实际耗时，四舍五入到一位小数。                  |
| `error`          | `str`/`None` | 非零退出或 `"timeout"`，否则为 `None`。         |

## `main()`

为 `SKILLS` 中的每个条目加载 `skills/<skill>/evals/eval_queries.json`，并为每个
用例构建一个任务。所有任务通过 `ThreadPoolExecutor(max_workers=3)` 运行。

该函数没有 docstring；此描述取自实现。

对于每个任务，按提交顺序打印：

```text
[i/N] <skill> PASS|FAIL expected=<bool> got=<bool> other=[...] <seconds>s
```

所有任务完成后，它将完整结果列表以两空格缩进写入 `/tmp/trigger-results.json`，
并为每个 skill 打印一个通过计数：

```text
<skill>: <passed>/<total>
```

## 相关

- 常量：[配置](configuration.zh.md)
- 结果字段：[结果](results.zh.md)
