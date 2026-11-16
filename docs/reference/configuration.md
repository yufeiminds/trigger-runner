# Configuration

The runner is configured by module-level constants in each script and by
`opencode.json` in the working directory. There are no command-line flags.

## `trigger_runner.py` constants

| Name       | Value                                                                      | Use                                                                 |
| ---------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `ROOT`     | `Path("/Users/yufei/workspace/github/yufeiminds/effective-skills")`        | Skill repository; queries are read from `skills/<skill>/evals/eval_queries.json`. |
| `EVAL_DIR` | `Path("/private/var/folders/4z/cwzzkq857rld3k2ssf3631yw0000gn/T/opencode/skill-eval")` | Working directory for each `opencode run`; holds `opencode.json`. |
| `MODEL`    | `"deepseek/deepseek-flash"`                                                | Model identifier passed to `opencode -m`.                          |
| `SKILLS`   | `["clean-code", "diataxis"]`                                               | Skills to evaluate, by directory name.                             |

## `trigger_runner2.py` constants

| Name       | Value                        | Use                                       |
| ---------- | ---------------------------- | ----------------------------------------- |
| `ROOT`     | same as `trigger_runner.py`  | Skill repository.                         |
| `EVAL_DIR` | same as `trigger_runner.py`  | Working directory for each `opencode run`. |
| `MODEL`    | `"deepseek/deepseek-flash"`  | Model identifier passed to `opencode -m`. |
| `SKILLS`   | `["clean-code", "diataxis"]` | Skills to evaluate.                       |
| `TIMEOUT`  | `120`                        | Per-session cap in seconds.               |

`trigger_runner.py` caps each session at 150 seconds; the constant is written
inline in the `subprocess.run` call rather than named.

## `opencode.json`

The configuration file in `EVAL_DIR` has these settings:

| Key                       | Value                                                             |
| ------------------------- | ----------------------------------------------------------------- |
| `permission.bash`         | `"deny"`                                                          |
| `permission.edit`         | `"deny"`                                                          |
| `permission.webfetch`     | `"deny"`                                                          |
| `providers.deepseek.name` | `"DeepSeek"`                                                      |
| `providers.deepseek.env`  | `["DEEPSEEK_API_KEY"]`                                            |
| `providers.deepseek.package` | `"@opencode/ai/providers/openai-compatible"`                   |
| `providers.deepseek.settings.baseURL` | `"https://api.deepseek.com/v1"`                        |
| `providers.deepseek.models` | `deepseek-flash`, named `"DeepSeek V4.1 Flash"`                 |

The schema reference is `https://opencode.ai/config.json`.

## Related

- Module behavior: [trigger_runner](trigger-runner.md), [trigger_runner2](second-pass-runner.md)
- Output formats: [Results](results.md)
