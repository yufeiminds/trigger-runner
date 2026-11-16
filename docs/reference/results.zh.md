# 结果

两个 runner 都会逐用例打印进度、为每个 skill 打印摘要，并将一个 JSON 数组写入
`/tmp`。

## 通过规则

当该 skill 的实际触发状态与 `should_trigger` 一致时，用例通过：

- 正例（`should_trigger: true`）：仅当 skill 被调用时通过。
- 负例（`should_trigger: false`）：仅当 skill 未被调用时通过。

记录的 `pass` 字段为 `triggered == should_trigger`。

## `trigger_runner.py` 控制台输出

逐用例：

```text
[i/N] <skill> PASS|FAIL expected=<bool> got=<bool> other=[...] <seconds>s
```

摘要：

```text
<skill>: <passed>/<total>
```

## `trigger_runner.py` JSON 记录

路径：`/tmp/trigger-results.json`。该文件是一个对象数组：

| 键               | 类型         | 说明                                            |
| ---------------- | ------------ | ----------------------------------------------- |
| `skill`          | `str`        | 被测 skill。                                    |
| `query`          | `str`        | 查询文本。                                      |
| `should_trigger` | `bool`       | 预期的触发状态。                                |
| `triggered`      | `bool`       | 该 skill 是否被调用。                           |
| `other_skill`    | `list[str]`  | 其他被调用且参与评估的 skill，已排序。          |
| `pass`           | `bool`       | `triggered == should_trigger`。                 |
| `seconds`        | `float`      | 实际耗时，四舍五入到一位小数。                  |
| `error`          | `str`/`None` | 非零退出、`"timeout"`，否则为 `None`。          |

## `trigger_runner2.py` 控制台输出

逐用例：

```text
[i/N] <skill> expected=<bool> got=<bool> timeout=<bool> <seconds>s
```

摘要：

```text
<skill>: <triggered>/<total> triggered
```

## `trigger_runner2.py` JSON 记录

路径：`/tmp/trigger-results-2.json`。该文件是一个对象数组：

| 键               | 类型         | 说明                                             |
| ---------------- | ------------ | ------------------------------------------------ |
| `skill`          | `str`        | 被测 skill。                                     |
| `query`          | `str`        | 查询文本。                                       |
| `should_trigger` | `bool`       | 预期的触发状态。                                 |
| `triggered`      | `bool`       | 该 skill 是否出现在解析后的输出中。              |
| `other_skill`    | `list[str]`  | 其他被调用且参与评估的 skill，已排序。           |
| `timed_out`      | `bool`       | 进程是否超过 `TIMEOUT`。                         |
| `seconds`        | `float`      | 实际耗时，四舍五入到一位小数。                   |
| `error`          | `str`/`None` | 异常文本，否则为 `None`。                        |

## 触发检测

调用信息从 JSON 事件流中读取。当某一行的 `part.type` 为 `"tool"` 且 `part.tool`
为 `"skill"` 时，该行计入；被调用的名称为 `part.state.input.name`。第一个 runner
会将这个名称与被测 skill 比较，并将 `SKILLS` 中的其他名称记录到 `other_skill`。
