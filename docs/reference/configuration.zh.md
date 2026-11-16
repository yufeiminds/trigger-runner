# 配置

runner 通过每个脚本中的模块级常量以及当前工作目录中的 `opencode.json` 进行配置。
没有命令行参数。

## `trigger_runner.py` 常量

| 名称       | 值                                                                         | 用途                                                                |
| ---------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `ROOT`     | `Path("/Users/yufei/workspace/github/yufeiminds/effective-skills")`        | skill 仓库；查询从 `skills/<skill>/evals/eval_queries.json` 读取。   |
| `EVAL_DIR` | `Path("/private/var/folders/4z/cwzzkq857rld3k2ssf3631yw0000gn/T/opencode/skill-eval")` | 每次 `opencode run` 的工作目录；存放 `opencode.json`。 |
| `MODEL`    | `"deepseek/deepseek-flash"`                                                | 传给 `opencode -m` 的模型标识符。                                   |
| `SKILLS`   | `["clean-code", "diataxis"]`                                               | 要评估的 skill，按目录名指定。                                      |

## `trigger_runner2.py` 常量

| 名称       | 值                           | 用途                                       |
| ---------- | ---------------------------- | ------------------------------------------ |
| `ROOT`     | 与 `trigger_runner.py` 相同  | skill 仓库。                               |
| `EVAL_DIR` | 与 `trigger_runner.py` 相同  | 每次 `opencode run` 的工作目录。           |
| `MODEL`    | `"deepseek/deepseek-flash"`  | 传给 `opencode -m` 的模型标识符。          |
| `SKILLS`   | `["clean-code", "diataxis"]` | 要评估的 skill。                           |
| `TIMEOUT`  | `120`                        | 每个会话的上限，单位为秒。                 |

`trigger_runner.py` 将每个会话上限设为 150 秒；该常量直接写在 `subprocess.run`
调用中，而没有被命名。

## `opencode.json`

`EVAL_DIR` 中的配置文件包含以下设置：

| 键                                    | 值                                                            |
| ------------------------------------- | ------------------------------------------------------------- |
| `permission.bash`                     | `"deny"`                                                      |
| `permission.edit`                     | `"deny"`                                                      |
| `permission.webfetch`                 | `"deny"`                                                      |
| `providers.deepseek.name`             | `"DeepSeek"`                                                  |
| `providers.deepseek.env`              | `["DEEPSEEK_API_KEY"]`                                        |
| `providers.deepseek.package`          | `"@opencode/ai/providers/openai-compatible"`                  |
| `providers.deepseek.settings.baseURL` | `"https://api.deepseek.com/v1"`                               |
| `providers.deepseek.models`           | `deepseek-flash`，名称为 `"DeepSeek V4.1 Flash"`              |

模式参考为 `https://opencode.ai/config.json`。

## 相关

- 模块行为：[trigger_runner](trigger-runner.zh.md)、[trigger_runner2](second-pass-runner.zh.md)
- 输出格式：[结果](results.zh.md)
