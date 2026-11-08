---
type: log
title: Log
---

# Log

> Append-only timeline. Newest at the bottom. Last entries: `grep "^## \[" log.md | tail -10`

## [2026-11-08] setup | Vault created from Second-Brain template
- created: AGENTS.md, index.md, log.md, 90-system/templates/*

## [2026-11-08] schema | Added linter and protect hook
- created: scripts/lint.py, .claude/hooks/protect_paths.py, .claude/settings.json · updated: AGENTS.md (§2, §4.4, §6), README.md

## [2026-11-08] schema | Added operation skills
- created: .agents/skills/{capture,ingest,query,lint,repair,project,brain-review,setup}/SKILL.md, .claude/skills → ../.agents/skills (symlink) · updated: AGENTS.md (§2, §4 now summarizes skills), README.md

## [2026-11-08] schema | Added second-brain router skill
- created: .agents/skills/second-brain/SKILL.md · updated: AGENTS.md §4, README.md

## [2026-11-08] schema | Removed protect hook
- removed: .claude/hooks/protect_paths.py, .claude/settings.json · updated: AGENTS.md §2 §6, README.md, prior-art.md, skills ingest + second-brain
