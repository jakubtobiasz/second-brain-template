---
name: lint
description: Health-check the second brain. Run the mechanical linter (scripts/lint.py), add a semantic review (contradictions, uncited claims, merge candidates, questions to explore), and save a ranked report to 50-outputs/lint/. Report-only, it never fixes anything. Use when the owner says "lint", "check vault health", "audit the wiki", "what's broken", or for the weekly/monthly maintenance pass.
---

# Lint: health check (report only)

**Never fix anything during lint.** Repair is a separate decision (the `repair` skill).

## 1. Mechanical pass
```bash
python3 scripts/lint.py --write
```
This saves `50-outputs/lint/YYYY-MM-DD-lint.md` with errors, warnings, and notes: broken links, frontmatter,
index coverage, orphans, one-way links, duplicates, stale seeds/state/inbox, and `raw-modified` (git).
Don't re-check by hand what the script covers. If the script fails to run, report that first.

## 2. Semantic pass
Fill the report's `## Semantic review (agent)` section. Don't read every page: sample smartly.
- **Contradictions**: pages on overlapping topics (shared links/tags) that state different facts with no
  `## Contradictions` section. Check pages updated recently against their neighbours.
- **Uncited claims**: specific numbers, dates, quotes without a nearby `[[source]]`. Spot-check ~10 pages,
  prioritizing `stable` pages and the most-linked hubs.
- **Lost caveats**: compare 2-3 recently ingested source pages with their raw files. Did hedges survive?
- **Scatter**: several pages covering one topic (merge candidates); **bloat**: one page covering many (split candidates).
- **Superseded state**: newer sources that changed a fact while other pages still describe the old one.
- **Missing pages**: people/concepts mentioned on 3+ pages without their own page.
- **Next questions & sources**: 3-5 questions the wiki can almost answer, plus the source that would close each gap.

## 3. Rank
Finish the report with `## Recommended order`: the top 5-10 fixes, ordered by what they unblock
(errors that break navigation first, then contradictions, then hygiene). Number them so the owner can say
"fix 1-3".

## 4. Log and report
- Append to `log.md`: `## [YYYY-MM-DD] lint | N errors, M warnings` + `- report: 50-outputs/lint/YYYY-MM-DD-lint.md`.
- Tell the owner the headline counts, the top 3 recommended fixes, and "say *fix 1-3* to repair".

## Hard constraints
- Report only: no edits outside `50-outputs/lint/` and `log.md`.
- Never "fix" `10-raw/` issues by editing raw files. A `raw-modified` finding means restore from git (owner decides).
