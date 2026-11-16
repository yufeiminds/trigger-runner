# trigger-runner

A small harness for measuring whether agent skills fire on the right requests.
For each `(query, should_trigger)` pair in a skill's `evals/eval_queries.json`,
it asks OpenCode — running a custom DeepSeek model — and records whether the
skill was actually invoked.

## Quickstart

You need Python 3.9+ (standard library only), [`opencode`](https://opencode.ai)
on `PATH`, a `DEEPSEEK_API_KEY`, and a skill repository containing
`skills/<name>/evals/eval_queries.json`.

1. Export the API key:

   ```shell
   export DEEPSEEK_API_KEY=...
   ```

2. Set `ROOT`, `EVAL_DIR`, and `SKILLS` at the top of `trigger_runner.py`.
   `ROOT` is the skill repository; `EVAL_DIR` holds `opencode.json` and must
   contain the same skills under `.opencode/skills/`.

3. Run it:

   ```shell
   python3 trigger_runner.py
   ```

You will see one line per case and a pass count per skill:

```text
[1/32] clean-code PASS expected=True got=True other=[] 12.4s
[2/32] clean-code FAIL expected=False got=True other=[] 9.8s
...
clean-code: 29/32
diataxis: 30/32
```

Full results land in `/tmp/trigger-results.json`. For sessions that may exceed
the timeout, use `trigger_runner2.py`, which keeps partial output and reports
raw trigger counts instead of pass/fail.

Follow the full walkthrough in
[docs/tutorials/run-your-first-evaluation.md](docs/tutorials/run-your-first-evaluation.md).

## What it evaluates

Each skill supplies a JSON array of cases:

```json
[
  { "query": "Break up this 1200-line handler file.", "should_trigger": true },
  { "query": "What time is it in Tokyo?", "should_trigger": false }
]
```

A case passes when the skill's observed trigger state matches `should_trigger`:
a positive case must invoke the skill, a negative case must not. Invocations are
detected from the OpenCode JSON event stream.

## Documentation

| Guide                                                         | Contents                                                  |
| ------------------------------------------------------------- | --------------------------------------------------------- |
| [Tutorial](docs/tutorials/run-your-first-evaluation.md)       | Clean checkout to a completed trigger evaluation           |
| [Configuration](docs/reference/configuration.md)              | Module constants and `opencode.json`                      |
| [trigger_runner](docs/reference/trigger-runner.md)            | `run_query()`, `main()`, and the command line             |
| [trigger_runner2](docs/reference/second-pass-runner.md)       | Timeout-tolerant second pass, including `TIMEOUT`         |
| [Results](docs/reference/results.md)                          | Console lines, JSON fields, and the pass rule             |

## Repository layout

| Path                 | Purpose                                                              |
| -------------------- | -------------------------------------------------------------------- |
| `trigger_runner.py`  | Main runner: per-case PASS/FAIL and a pass rate per skill             |
| `trigger_runner2.py` | Timeout-tolerant variant: keeps partial output and reports raw trigger counts |
| `skill-eval/`        | OpenCode workspace used as `EVAL_DIR`; holds the provider config and installed skills |
| `docs/`              | Tutorials and reference pages                                         |
| `README.zh.md`       | Chinese translation of this document                                  |
| `anthropics-skills/`, `skilltest/`, `skillinit/` | Local skill checkouts and scratch workspaces used while developing skills |

## Limitations

- One run per query, so results include model and sampling noise; rerun before
  treating a single failure as a regression.
- Paths, model, timeout, and skill list are hardcoded — this is a one-off
  harness, not a configurable CLI.
- It only measures triggering. Output quality lives in `evals/evals.json`.
- Provider errors and timeouts can look like missed triggers. Check the `error`
  and `timed_out` fields before concluding that a skill failed to fire.
- Every case is a paid model session; a full pass over many skills costs real
  time and tokens.
