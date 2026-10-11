#!/usr/bin/env python3
"""Summarize a published Spark sampler tree; does not contact the Minecraft server.

Only aggregate stack times and method names are written to the report. Raw Spark
JSON contains server metadata, so it is never committed or uploaded as artifact.
"""
import json
import sys
import urllib.request
from collections import defaultdict

CODE = "u5aki9eatL"
URL = f"https://spark.lucko.me/{CODE}?raw=1&full=1"


def label(node):
    return f"{node.get('className', '?')}.{node.get('methodName', '?')}"


def summarize(data):
    lines = ["# Spark CPU profile: server thread (60 s, 1 player)", "",
             f"Source: https://spark.lucko.me/{CODE} (full raw export)",
             "Live JAR unchanged. This is diagnostic sampling, not an A/B benchmark.",
             "Times below are sampled stack weights, not per-tick costs or proof of speedup.", ""]
    threads = data.get("threads", [])
    if not threads:
        raise ValueError("full Spark export has no thread tree (check full=1)")
    for thread in threads:
        if thread.get("name") != "Server thread":
            continue
        total = thread.get("time", 0)
        lines += [f"## {thread['name']}: {total:.1f} ms sampled", "",
                  "### Widest direct branches", ""]
        for node in sorted(thread.get("children", []), key=lambda x: x.get("time", 0), reverse=True)[:12]:
            lines.append(f"- {node.get('time', 0):.1f} ms ({node.get('time', 0)/total:.1%}): `{label(node)}`")
        inclusive = defaultdict(float)
        exclusive = defaultdict(float)
        counts = defaultdict(int)
        branch_paths = []

        def walk(node, path, depth):
            if depth > 200:
                raise ValueError("unexpectedly deep Spark profile")
            time = node.get("time", 0) or 0
            children = node.get("children", [])
            name = label(node)
            incl_key = name
            inclusive[incl_key] += time
            # An identical method in recursive/nested stacks is counted more than
            # once in inclusive totals; exclusive weights are the safer ranking.
            remainder = max(0, time - sum(c.get("time", 0) or 0 for c in children))
            exclusive[name] += remainder
            counts[name] += 1
            if time > total * .01 and (not children or remainder > total * .01):
                branch_paths.append((time, remainder, path + [name]))
            for child in children:
                walk(child, path + [name], depth + 1)

        for child in thread.get("children", []):
            walk(child, [], 0)
        lines += ["", "### Top self-time methods (child weights subtracted)", ""]
        for name, value in sorted(exclusive.items(), key=lambda kv: -kv[1])[:30]:
            lines.append(f"- {value:.1f} ms ({value/total:.1%}): `{name}`")
        lines += ["", "### Notable paths ending in a >=1% self-time frame", ""]
        for _, value, path in sorted(branch_paths, key=lambda x: -x[1])[:18]:
            lines.append(f"- {value:.1f} ms self: `{' -> '.join(path[-7:])}`")
        lines += ["", f"Nodes: {sum(counts.values())}; distinct methods: {len(counts)}.",
                  "Spark sample time includes waiting/parking if those frames were sampled; do not treat it as 50 s of CPU.", ""]
        return "\n".join(lines)
    raise ValueError("Server thread missing")


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "CUANTIC-profiler-analysis/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read(30_000_001)
    if len(raw) > 30_000_000:
        raise ValueError("Spark response exceeded 30 MB")
    data = json.loads(raw)
    if data.get("type") != "sampler":
        raise ValueError("not a Spark sampler export")
    with open(sys.argv[1], "w") as out:
        out.write(summarize(data))


if __name__ == "__main__":
    main()
