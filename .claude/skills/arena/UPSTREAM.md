# arena-skill: project-local installation

- Upstream: https://github.com/Jakeschincariol/arena-skill
- Pinned commit: `df07b8e518e10cdecd8cd7712d9958b6f396250e` (2026-09-26).
- License: MIT; upstream notice preserved in `LICENSE`.
- Vendored unchanged: `SKILL.md`, `bracket.py`, `rubric.md`, `strategies.json` from upstream `skills/arena/`.
- Installation location: `.claude/skills/arena/`, as documented by upstream for project-local Claude Code skills.

The full `/arena` bracket requires **Claude Code's Agent/Task tool**. This Arena.ai API session does not expose that tool, so installing the skill does not create 16 or 100 independent subagents here. The rubric can still be applied manually to every answer; do not claim a tournament ran when it did not. To run `/arena` in Claude Code, open this repository there. The default tournament is expensive (100 competitors, ~595 subagent calls); `--quick` is 16 competitors and ~91 calls. Never start one automatically for every short reply without a budget decision.

The skill writes tournament state into `.arena/`, ignored by Git. Do not include private server files, credentials, player data or licensed JARs in a task file or send them to subagents.
