# 运行你的第一次触发评估

测试两个随附的 skill——`clean-code` 和 `diataxis`——是否会在它们本应服务的请求上
触发。runner 会把每个查询发送给 OpenCode，并记录该 skill 是否被调用。请预留几分钟：
每个查询都有独立的会话，最多同时运行三个会话。

## 准备工作

- Python 3.9 或更高版本；runner 只使用标准库。
- `opencode` 在 `PATH` 中。
- 环境变量 `DEEPSEEK_API_KEY`。
- 一个 skill 仓库，其中存在 `skills/<name>/evals/eval_queries.json` 文件。

## 让 runner 指向你的文件

打开 `trigger_runner.py`，设置顶部的四个常量。`ROOT` 是包含 `skills/` 的仓库；
`EVAL_DIR` 是存放会话运行所用 `opencode.json` 的目录。

```python
ROOT = Path("/path/to/skill-repo")
EVAL_DIR = Path("/path/to/skill-eval")
MODEL = "deepseek/deepseek-flash"
SKILLS = ["clean-code", "diataxis"]
```

检查两个文件是否确实位于你指定的位置：

```shell
test -f /path/to/skill-eval/opencode.json && echo "config ok"
for skill in clean-code diataxis; do
  test -f "/path/to/skill-repo/skills/$skill/evals/eval_queries.json" \
    && echo "$skill: queries ok"
done
```

你应该会看到每个文件一行输出：

```text
config ok
clean-code: queries ok
diataxis: queries ok
```

缺少某一行意味着该路径有误。继续之前先修正它；当查询文件不存在时，runner 会以
traceback 停止。

## 导出 API key

在将要运行该测试工具的同一个 shell 中：

```shell
export DEEPSEEK_API_KEY=...
```

询问 shell 能否看到该变量：

```shell
test -n "$DEEPSEEK_API_KEY" && echo set
```

它会打印 `set`。如果没有任何输出，则说明变量为空，或者是在另一个 shell 中导出的。

## 启动运行

```shell
python3 trigger_runner.py
```

让它继续运行。每个会话上限为 150 秒，超时会被视为未触发。

## 随每个用例的完成读取结果

每个完成的用例打印一行：

```text
[7/64] clean-code PASS expected=false got=false other=['diataxis'] 9.8s
```

`PASS` 表示实际发生的情况与 `should_trigger` 一致。`got` 表示该 skill 是否触发，
`other` 列出其他被评估且触发了的 skill。在上面这一行中，`clean-code` 不应触发且
确实未触发，而 `diataxis` 触发了。

## 读取最终得分

最后一个用例结束后，runner 会为每个 skill 打印通过计数：

```text
clean-code: 29/32
diataxis: 30/32
```

每一行读作 通过数/总数。数值在多次运行之间会有所波动；单次失败本身并不构成回归。

## 找出失败用例

runner 已将每个用例写入 `/tmp/trigger-results.json`。列出未通过的用例及其查询：

```shell
python3 - <<'PY'
import json

for r in json.load(open("/tmp/trigger-results.json")):
    if r["pass"]:
        continue
    print(f'{r["skill"]}: expected={r["should_trigger"]} '
          f'got={r["triggered"]} error={r["error"]}')
    print(f'  {r["query"]}')
PY
```

每个失败会打印 skill、预期、实际发生的情况以及任何错误，随后是查询文本。`error`
为 `"timeout"` 或退出码表示会话失败，而不是 skill 误判了请求。

## 重跑失败用例

保留第一次的结果以便比较：

```shell
cp /tmp/trigger-results.json /tmp/trigger-results-1.json
```

在 `trigger_runner.py` 中把 `SKILLS` 缩小到你正在追查的 skill：

```python
SKILLS = ["clean-code"]
```

再次运行该测试工具。第一次失败而重跑通过的用例属于噪声；两次都失败的用例值得
调查。各字段的含义列在[结果](../reference/results.zh.md)中。

## 下一步

- 要更改模型、skill 列表或路径，请参阅[配置](../reference/configuration.zh.md)。
- 要查看运行背后的函数，请参阅
  [trigger_runner 模块](../reference/trigger-runner.zh.md)。
