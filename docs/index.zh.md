# trigger-runner

trigger-runner 衡量 agent skill 是否在其本应服务的请求上触发。对于某个 skill 的
`evals/eval_queries.json` 中的每个 `(query, should_trigger)` 二元组，它都会通过
OpenCode 运行该查询，并记录该 skill 是否被调用。

该测试工具只衡量触发情况。输出质量在 `evals/evals.json` 中单独评估，且每个查询
只运行一次，结果会包含模型和采样噪声。

## 从这里开始

- [教程](tutorials/index.zh.md)——跟随一课，从干净检出走到完成一次触发评估。
- [参考](reference/index.zh.md)——查阅模块函数、配置常量和结果格式。
