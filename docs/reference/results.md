# Results

Both runners print progress per case, print a summary per skill, and write a
JSON array to `/tmp`.

## Pass rule

A case passes when the skill's observed trigger state matches `should_trigger`:

- Positive case (`should_trigger: true`): passes only if the skill is invoked.
- Negative case (`should_trigger: false`): passes only if the skill is not
  invoked.

The record's `pass` field is `triggered == should_trigger`.

## `trigger_runner.py` console output

Per case:

```text
[i/N] <skill> PASS|FAIL expected=<bool> got=<bool> other=[...] <seconds>s
```

Summary:

```text
<skill>: <passed>/<total>
```

## `trigger_runner.py` JSON record

Path: `/tmp/trigger-results.json`. The file is an array of objects:

| Key              | Type         | Description                                     |
| ---------------- | ------------ | ----------------------------------------------- |
| `skill`          | `str`        | Skill under test.                               |
| `query`          | `str`        | Query text.                                     |
| `should_trigger` | `bool`       | Expected trigger state.                         |
| `triggered`      | `bool`       | Whether the skill was invoked.                  |
| `other_skill`    | `list[str]`  | Other evaluated skills invoked, sorted.         |
| `pass`           | `bool`       | `triggered == should_trigger`.                  |
| `seconds`        | `float`      | Wall-clock duration, rounded to one decimal.    |
| `error`          | `str`/`None` | Non-zero exit, `"timeout"`, otherwise `None`.   |

## `trigger_runner2.py` console output

Per case:

```text
[i/N] <skill> expected=<bool> got=<bool> timeout=<bool> <seconds>s
```

Summary:

```text
<skill>: <triggered>/<total> triggered
```

## `trigger_runner2.py` JSON record

Path: `/tmp/trigger-results-2.json`. The file is an array of objects:

| Key              | Type         | Description                                      |
| ---------------- | ------------ | ------------------------------------------------ |
| `skill`          | `str`        | Skill under test.                                |
| `query`          | `str`        | Query text.                                      |
| `should_trigger` | `bool`       | Expected trigger state.                          |
| `triggered`      | `bool`       | Whether the skill appears in the parsed output.  |
| `other_skill`    | `list[str]`  | Other evaluated skills invoked, sorted.          |
| `timed_out`      | `bool`       | Whether the process exceeded `TIMEOUT`.          |
| `seconds`        | `float`      | Wall-clock duration, rounded to one decimal.     |
| `error`          | `str`/`None` | Exception text, otherwise `None`.                |

## Trigger detection

Invocations are read from the JSON event stream. A line counts when its
`part.type` is `"tool"` and its `part.tool` is `"skill"`; the invoked name is
`part.state.input.name`. The first runner compares that name with the skill under
test and records other names from `SKILLS` in `other_skill`.
