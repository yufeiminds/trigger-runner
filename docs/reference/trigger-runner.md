# `trigger_runner` module

> One-off trigger-eval runner using OpenCode + a custom DeepSeek provider.

The module evaluates whether agent skills are invoked for the right queries by
running each query through `opencode run` and inspecting the JSON event stream
for `skill` tool calls.

## Invocation

```text
python3 trigger_runner.py
```

## `run_query(skill, item)`

Runs one `(query, should_trigger)` case and returns a result record.

The function has no docstring; this description is taken from the
implementation.

| Parameter | Type   | Description                                 |
| --------- | ------ | ------------------------------------------- |
| `skill`   | `str`  | Skill name to look for in the event stream. |
| `item`    | `dict` | Case with `query` and `should_trigger` keys. |

The function executes the argument vector
`opencode run --format json --auto -m <MODEL> <query>` in `EVAL_DIR` with a
150-second timeout. Each line of standard output is parsed as JSON. A line
contributes a call when its `part.type` is `"tool"` and its `part.tool` is
`"skill"`; the call's name is `part.state.input.name`. A name equal to `skill`
sets `triggered`, and any other name in `SKILLS` is added to `others`.

A non-zero exit contributes an error of the form
`exit <code>: <first 200 characters of stderr>`. A `TimeoutExpired` exception
contributes the error `"timeout"`.

The return value is a `dict`:

| Key              | Type         | Description                                     |
| ---------------- | ------------ | ----------------------------------------------- |
| `skill`          | `str`        | Skill under test.                               |
| `query`          | `str`        | Query text.                                     |
| `should_trigger` | `bool`       | Expected trigger state.                         |
| `triggered`      | `bool`       | Whether the skill was invoked.                  |
| `other_skill`    | `list[str]`  | Other evaluated skills invoked, sorted.         |
| `pass`           | `bool`       | `triggered == should_trigger`.                  |
| `seconds`        | `float`      | Wall-clock duration, rounded to one decimal.    |
| `error`          | `str`/`None` | Non-zero exit or `"timeout"`, otherwise `None`. |

## `main()`

Loads `skills/<skill>/evals/eval_queries.json` for every entry in `SKILLS` and
builds one task per case. All tasks run through a
`ThreadPoolExecutor(max_workers=3)`.

The function has no docstring; this description is taken from the
implementation.

For each task, in submission order, it prints:

```text
[i/N] <skill> PASS|FAIL expected=<bool> got=<bool> other=[...] <seconds>s
```

After all tasks, it writes the full result list to
`/tmp/trigger-results.json` with two-space indentation and prints one pass count
per skill:

```text
<skill>: <passed>/<total>
```

## Related

- Constants: [Configuration](configuration.md)
- Result fields: [Results](results.md)
