---
name: brain-review
description: Run a daily or weekly review of the second brain. Read recent journal entries, log.md, inbox and active projects, then propose what to promote into the wiki, which tasks and open loops need attention, and what to ingest next. Proposes only, it applies nothing without approval. Use when the owner says "daily review", "weekly review", "what's on my plate", "what did I miss", or "process my journal".
---

# Review: daily / weekly

You read; the owner decides. Never edit `40-journal/`.

## Window
- **Daily**: since the last review entry in `log.md` (or the last 1-2 days).
- **Weekly**: last 7 days. Default to weekly if unspecified and it's been more than 3 days.
- Find the last review: `grep "^## \[.*\] review" log.md | tail -1`.

## Gather
1. Journal entries in the window: `40-journal/YYYY-MM-DD.md` (Ideas and Tasks sections especially).
2. `log.md` entries in the window: what was ingested, asked, changed.
3. Inbox: items waiting, oldest first, with age.
4. Active projects: last log entry date + `Next:` items; flag projects silent for more than 14 days.
5. Recent `50-outputs/queries/` with `filed_back: false`.

## Write the review
Save to `50-outputs/queries/YYYY-MM-DD-weekly-review.md` (or `-daily-review`) with `type: query`:
```markdown
# Weekly review: YYYY-MM-DD

## Highlights
- 3-5 bullets: what moved this week (ingests, decisions, insights), with links.

## Promote to wiki (proposed)
- [ ] Journal idea "<…>" ([[40-journal/2026-…]]) → new/updated page [[…]]
- [ ] Query answer [[50-outputs/queries/…]] → file back as synthesis

## Open loops
- [ ] Task/commitment from journal or project logs, with link. Re-check it isn't already done before listing it.

## Projects
| Project | Last update | Next | Flag |

## Inbox (N items)
- oldest first, with age and a suggestion: ingest / archive / ask

## Suggested focus
- 1-3 things for the next period.
```

## Then
- Log: `## [YYYY-MM-DD] review | weekly` + `- saved: …`.
- Ask which proposals to act on. Promotions run through the normal rules (citations, links, index, log).
  Tasks move to project logs or stay in the owner's journal (the owner writes that).

## Hard constraints
- Never edit journal files. Quote or link them instead.
- Propose; don't apply. The owner checks the boxes.
