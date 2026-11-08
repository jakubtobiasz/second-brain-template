---
name: repair
description: Apply owner-approved fixes from a second brain lint report, one item at a time, with logging. Use when the owner says "fix 1-3", "repair the lint findings", "merge these duplicate pages", "fix the broken links", or approves items from a report in 50-outputs/lint/.
---

# Repair: apply approved lint fixes

Only fix what the owner approved. Use the latest report in `50-outputs/lint/` unless told otherwise.

## Steps
1. Open the report; list the approved items back in one line each ("Fixing: 1) broken link …, 2) …").
2. For each item, in order:
   - Read every page involved **before** editing.
   - Apply the smallest fix that resolves it (patterns below).
   - Note what you did next to the item in the report: `✔ fixed: <how>` (or `✘ skipped: <why>`).
3. Run `python3 scripts/lint.py` and confirm the fixed items are gone and nothing new broke.
4. Append to `log.md`: `## [YYYY-MM-DD] repair | items 1-3 from YYYY-MM-DD-lint` with created/updated pages.
5. Suggest a commit: `git commit -am "repair: <summary>"`.

## Fix patterns
| Finding | Fix |
|---|---|
| broken-link | Fix the typo, or create a `seed` page for the target (frontmatter, one-line summary, link back) |
| not in index | Add the `index.md` line |
| frontmatter | Add the missing fields; never invent `sources`. Downgrade to `seed` if there are none |
| orphan | Link it from 1-2 genuinely related pages (with a reason), or propose deprecation |
| one-way-link | Add the back-reference with a short "why" in `## Related` |
| duplicate | **Merge**: pick the canonical page (more links/content), move unique content + sources into it, add the other's title to `aliases`, set the other to `status: deprecated` + `superseded_by: "[[canonical]]"`, repoint inbound links |
| stale-state | Re-check sources; update with a new as-of date, or mark "(unverified since YYYY-MM-DD)" |
| stale-seed | Grow from existing sources, merge, or deprecate (ask which) |
| contradiction | Add a `## Contradictions` section; don't pick a winner unless a newer/stronger source settles it |
| raw-modified | Don't touch. Tell the owner: `git checkout -- <file>` restores it |

## Renames and moves
Use `git mv old new`, then update every inbound link: `grep -rl "\[\[old-name" --include=*.md .` → edit each.
Rename = check in with the owner first (AGENTS.md §6 rule 7).

## Hard constraints
- One approved item at a time; anything beyond the approved list goes back to the owner.
- Never delete pages: deprecate. Never edit `10-raw/` or `40-journal/`.
- More than 5 files affected by one item → show the plan and wait.
