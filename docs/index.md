# trigger-runner

trigger-runner measures whether agent skills fire on the requests they are meant
to serve. For each `(query, should_trigger)` pair in a skill's
`evals/eval_queries.json`, it runs the query through OpenCode and records
whether the skill was invoked.

The harness measures triggering only. Output quality is evaluated separately in
`evals/evals.json`, and a single run per query includes model and sampling
noise.

## Start here

- [Tutorials](tutorials/index.md) — follow a lesson from a clean checkout to a
  completed trigger evaluation.
- [Reference](reference/index.md) — look up module functions, configuration
  constants, and result formats.
