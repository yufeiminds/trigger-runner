#!/usr/bin/env python3
"""One-off trigger-eval runner using OpenCode + a custom DeepSeek provider."""

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path("/Users/yufei/workspace/github/yufeiminds/effective-skills")
EVAL_DIR = Path("/private/var/folders/4z/cwzzkq857rld3k2ssf3631yw0000gn/T/opencode/skill-eval")
MODEL = "deepseek/deepseek-flash"
SKILLS = ["clean-code", "diataxis"]


def run_query(skill, item):
    query = item["query"]
    expected = item["should_trigger"]
    cmd = [
        "opencode", "run", "--format", "json", "--auto",
        "-m", MODEL, query,
    ]
    started = time.time()
    triggered = set()
    others = set()
    error = None
    try:
        proc = subprocess.run(
            cmd, cwd=EVAL_DIR, capture_output=True, text=True, timeout=150
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            part = event.get("part", {})
            if part.get("type") != "tool" or part.get("tool") != "skill":
                continue
            name = (part.get("state", {}).get("input") or {}).get("name", "")
            if name == skill:
                triggered.add(name)
            elif name in SKILLS:
                others.add(name)
        if proc.returncode != 0:
            error = f"exit {proc.returncode}: {proc.stderr[:200]}"
    except subprocess.TimeoutExpired:
        error = "timeout"
    duration = round(time.time() - started, 1)
    passed = (skill in triggered) == bool(expected)
    return {
        "skill": skill,
        "query": query,
        "should_trigger": bool(expected),
        "triggered": skill in triggered,
        "other_skill": sorted(others),
        "pass": passed,
        "seconds": duration,
        "error": error,
    }


def main():
    tasks = []
    for skill in SKILLS:
        queries = json.loads((ROOT / "skills" / skill / "evals" / "eval_queries.json").read_text())
        for item in queries:
            tasks.append((skill, item))

    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(run_query, skill, item) for skill, item in tasks]
        for i, future in enumerate(futures, 1):
            result = future.result()
            results.append(result)
            print(
                f"[{i}/{len(futures)}] {result['skill']} "
                f"{'PASS' if result['pass'] else 'FAIL'} "
                f"expected={result['should_trigger']} got={result['triggered']} "
                f"other={result['other_skill']} {result['seconds']}s",
                flush=True,
            )

    Path("/tmp/trigger-results.json").write_text(json.dumps(results, indent=2))
    for skill in SKILLS:
        subset = [r for r in results if r["skill"] == skill]
        passed = sum(1 for r in subset if r["pass"])
        print(f"{skill}: {passed}/{len(subset)}")


if __name__ == "__main__":
    main()
