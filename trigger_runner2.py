#!/usr/bin/env python3
"""Second trigger-eval pass: captures partial output on timeout."""

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path("/Users/yufei/workspace/github/yufeiminds/effective-skills")
EVAL_DIR = Path("/private/var/folders/4z/cwzzkq857rld3k2ssf3631yw0000gn/T/opencode/skill-eval")
MODEL = "deepseek/deepseek-flash"
SKILLS = ["clean-code", "diataxis"]
TIMEOUT = 120


def parse_events(output):
    triggered = set()
    others = set()
    for line in output.splitlines():
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
        if name in SKILLS:
            triggered.add(name)
    return triggered


def run_query(skill, item):
    query = item["query"]
    expected = item["should_trigger"]
    started = time.time()
    timed_out = False
    try:
        proc = subprocess.Popen(
            ["opencode", "run", "--format", "json", "--auto", "-m", MODEL, query],
            cwd=EVAL_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        try:
            out, _ = proc.communicate(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, _ = proc.communicate()
            timed_out = True
    except Exception as exc:  # noqa: BLE001
        return {
            "skill": skill, "query": query, "should_trigger": bool(expected),
            "triggered": False, "other_skill": [], "timed_out": True,
            "seconds": round(time.time() - started, 1), "error": str(exc),
        }

    seen = parse_events(out)
    return {
        "skill": skill,
        "query": query,
        "should_trigger": bool(expected),
        "triggered": skill in seen,
        "other_skill": sorted(seen - {skill}),
        "timed_out": timed_out,
        "seconds": round(time.time() - started, 1),
        "error": None,
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
                f"expected={result['should_trigger']} got={result['triggered']} "
                f"timeout={result['timed_out']} {result['seconds']}s",
                flush=True,
            )

    Path("/tmp/trigger-results-2.json").write_text(json.dumps(results, indent=2))
    for skill in SKILLS:
        subset = [r for r in results if r["skill"] == skill]
        print(f"{skill}: {sum(1 for r in subset if r['triggered'])}/{len(subset)} triggered")


if __name__ == "__main__":
    main()
