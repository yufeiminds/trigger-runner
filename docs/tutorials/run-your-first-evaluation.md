# Run your first trigger evaluation

Test whether two bundled skills, `clean-code` and `diataxis`, fire on the
requests they are meant to serve. The runner sends each query to OpenCode and
records whether the skill was invoked. Budget a few minutes: every query gets
its own session, and up to three sessions run at once.

## What you need

- Python 3.9 or later; the runner uses only the standard library.
- `opencode` on `PATH`.
- A `DEEPSEEK_API_KEY` environment variable.
- A skill repository whose `skills/<name>/evals/eval_queries.json` files exist.

## Point the runner at your files

Open `trigger_runner.py` and set the four constants at the top. `ROOT` is the
repository that holds `skills/`; `EVAL_DIR` is the directory that holds the
`opencode.json` the sessions run in.

```python
ROOT = Path("/path/to/skill-repo")
EVAL_DIR = Path("/path/to/skill-eval")
MODEL = "deepseek/deepseek-flash"
SKILLS = ["clean-code", "diataxis"]
```

Check that both files are where you say they are:

```shell
test -f /path/to/skill-eval/opencode.json && echo "config ok"
for skill in clean-code diataxis; do
  test -f "/path/to/skill-repo/skills/$skill/evals/eval_queries.json" \
    && echo "$skill: queries ok"
done
```

You should see one line per file:

```text
config ok
clean-code: queries ok
diataxis: queries ok
```

A missing line means that path is wrong. Fix it before continuing; the runner
stops with a traceback when a query file is absent.

## Export your API key

In the same shell that will run the harness:

```shell
export DEEPSEEK_API_KEY=...
```

Ask the shell whether it can see the variable:

```shell
test -n "$DEEPSEEK_API_KEY" && echo set
```

It prints `set`. If it prints nothing, the variable is empty or was exported in
a different shell.

## Start the run

```shell
python3 trigger_runner.py
```

Leave it running. Each session is capped at 150 seconds, and a timeout counts as
a missed trigger.

## Read each case as it lands

Every finished case prints one line:

```text
[7/64] clean-code PASS expected=false got=false other=['diataxis'] 9.8s
```

`PASS` means what happened matched `should_trigger`. `got` is whether the skill
fired, and `other` lists the other evaluated skills that fired. In the line
above, `clean-code` was not expected to fire and did not, while `diataxis` did.

## Read the final score

After the last case, the runner prints a pass count for each skill:

```text
clean-code: 29/32
diataxis: 30/32
```

Read each line as passed/total. Expect the numbers to move between runs; one
failure is not by itself a regression.

## Find the failures

The runner wrote every case to `/tmp/trigger-results.json`. List the cases that
did not pass, with their queries:

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

Each failure prints the skill, the expectation, what happened, and any error,
followed by the query text. An `error` of `"timeout"` or an exit code means the
session failed rather than the skill misjudging the request.

## Rerun a failure

Keep the first results so you can compare:

```shell
cp /tmp/trigger-results.json /tmp/trigger-results-1.json
```

Narrow `SKILLS` in `trigger_runner.py` to the skill you are chasing:

```python
SKILLS = ["clean-code"]
```

Run the harness again. A case that failed once and passes on the rerun was
noise; a case that fails both times is worth investigating. The field meanings
are listed in [Results](../reference/results.md).

## Where to go next

- To change the model, skill list, or paths, see
  [Configuration](../reference/configuration.md).
- To inspect the functions behind the run, see the
  [trigger_runner module](../reference/trigger-runner.md).
