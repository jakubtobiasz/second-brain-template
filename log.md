---
type: log
title: Log
---

# Log

> Append-only timeline. Newest at the bottom. Last entries: `grep "^## \[" log.md | tail -10`
> Entry format: `## [YYYY-MM-DD] <operation> | <title>` (operations: ingest, query, lint, repair, project,
> review, gaps, schema, setup). The `setup` skill writes the first entry.
