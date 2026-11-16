# `trigger_runner2` module

> Second trigger-eval pass: captures partial output on timeout.

The module runs the same `(query, should_trigger)` cases as `trigger_runner`,
but keeps the output produced before a timeout instead of discarding the
session.

## Invocation

```text
python3 trigger_runner2.py
```

## `parse_events(output)`

Takes raw OpenCode output and returns the set of skill names invoked. A line
contributes a name when its `part.type` is `"tool"`, its `part.tool` is
`"skill"`, and `part.state.input.name` is present. Every name in `SKILLS` is
added to the set; the function does not separate the skill under test from the
others.

## `run_query(skill, item)`

Runs one case and returns a result record.

| Parameter | Type   | Description                                 |
| --------- | ------ | ------------------------------------------- |
| `skill`   | `str`  | Skill name to look for in the event stream. |
| `item`    | `dict` | Case with `query` and `should_trigger` keys. |

The function starts `opencode run --format json --auto -m <MODEL> <query>` with
`stdout` captured and `stderr` discarded, in `EVAL_DIR`. It waits up to
`TIMEOUT` seconds. On expiry it kills the process, collects the remaining
output, and sets `timed_out` to `True`. An exception during process startup
returns a record with `timed_out: True` and the exception text in `error`.

The return value is a `dict`:

| Key              | Type         | Description                                      |
| ---------------- | ------------ | ------------------------------------------------ |
| `skill`          | `str`        | Skill under test.                                |
| `query`          | `str`        | Query text.                                      |
| `should_trigger` | `bool`       | Expected trigger state.                          |
| `triggered`      | `bool`       | Whether the skill appears in `parse_events()`.   |
| `other_skill`    | `list[str]`  | Other evaluated skills invoked, sorted.          |
| `timed_out`      | `bool`       | Whether the process exceeded `TIMEOUT`.          |
| `seconds`        | `float`      | Wall-clock duration, rounded to one decimal.     |
| `error`          | `str`/`None` | Exception text, otherwise `None`.                |

A non-zero exit code is not recorded in `error`; the parsed output still
contributes to `triggered`.

## `main()`

Loads `skills/<skill>/evals/eval_queries.json` for every entry in `SKILLS` and
runs the tasks through a `ThreadPoolExecutor(max_workers=3)`.

For each task, in submission order, it prints:

```text
[i/N] <skill> expected=<bool> got=<bool> timeout=<bool> <seconds>s
```

It writes the full result list to `/tmp/trigger-results-2.json` with two-space
indentation. The final summary is a triggered count, not a pass count:

```text
<skill>: <triggered>/<total> triggered
```

## Related

- Constants, including `TIMEOUT`: [Configuration](configuration.md)
- Result fields: [Results](results.md)
