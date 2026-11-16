# `trigger_runner2` 模块

> 第二遍触发评估：在超时时捕获部分输出。

该模块运行与 `trigger_runner` 相同的 `(query, should_trigger)` 用例，但会保留
超时之前产生的输出，而不是丢弃整个会话。

## 调用方式

```text
python3 trigger_runner2.py
```

## `parse_events(output)`

接收原始 OpenCode 输出，返回被调用的 skill 名称集合。当某一行的 `part.type` 为
`"tool"`、`part.tool` 为 `"skill"` 且存在 `part.state.input.name` 时，该行贡献
一个名称。`SKILLS` 中的每个名称都会被加入集合；该函数不区分被测 skill 与其他
skill。

## `run_query(skill, item)`

运行一个用例并返回一条结果记录。

| 参数    | 类型   | 说明                                        |
| ------- | ------ | ------------------------------------------- |
| `skill` | `str`  | 要在事件流中查找的 skill 名称。             |
| `item`  | `dict` | 包含 `query` 和 `should_trigger` 键的用例。 |

该函数在 `EVAL_DIR` 中启动
`opencode run --format json --auto -m <MODEL> <query>`，捕获 `stdout` 并丢弃
`stderr`。它最多等待 `TIMEOUT` 秒。超时后它会终止进程、收集剩余输出，并将
`timed_out` 设为 `True`。进程启动期间发生异常时，返回的记录中 `timed_out: True`，
且 `error` 为异常文本。

返回值为 `dict`：

| 键               | 类型         | 说明                                             |
| ---------------- | ------------ | ------------------------------------------------ |
| `skill`          | `str`        | 被测 skill。                                     |
| `query`          | `str`        | 查询文本。                                       |
| `should_trigger` | `bool`       | 预期的触发状态。                                 |
| `triggered`      | `bool`       | 该 skill 是否出现在 `parse_events()` 中。        |
| `other_skill`    | `list[str]`  | 其他被调用且参与评估的 skill，已排序。           |
| `timed_out`      | `bool`       | 进程是否超过 `TIMEOUT`。                         |
| `seconds`        | `float`      | 实际耗时，四舍五入到一位小数。                   |
| `error`          | `str`/`None` | 异常文本，否则为 `None`。                        |

非零退出码不会记录到 `error` 中；解析出的输出仍会用于判断 `triggered`。

## `main()`

为 `SKILLS` 中的每个条目加载 `skills/<skill>/evals/eval_queries.json`，并通过
`ThreadPoolExecutor(max_workers=3)` 运行这些任务。

对于每个任务，按提交顺序打印：

```text
[i/N] <skill> expected=<bool> got=<bool> timeout=<bool> <seconds>s
```

它将完整结果列表以两空格缩进写入 `/tmp/trigger-results-2.json`。最终摘要统计的
是触发计数，而非通过计数：

```text
<skill>: <triggered>/<total> triggered
```

## 相关

- 常量（包括 `TIMEOUT`）：[配置](configuration.zh.md)
- 结果字段：[结果](results.zh.md)
