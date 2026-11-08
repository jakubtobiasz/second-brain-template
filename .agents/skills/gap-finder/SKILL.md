---
name: gap-finder
description: Find what the second brain doesn't know yet and turn it into a ranked reading list. Collects open questions, Gaps sections from saved answers, wanted (linked but missing) pages, thin single-source pages, seeds, contradictions and journal ideas, ranks them against the owner's current focus, and proposes concrete sources or searches. Use when the owner asks "what should I read next?", "what are my knowledge gaps?", "what's missing in my wiki?", "where should I dig deeper?", or "find sources for X".
---

# Gap-finder: what to learn next

Turns scattered "we don't know yet" signals into a short, ranked plan. **Proposes only.** Capturing sources
and ingesting them happen through `capture` / `ingest` with the owner's OK.

## 1. Collect (mechanical)
```bash
python3 scripts/gaps.py            # or --json
```
This lists signals with the pages they came from: query gaps, open questions, wanted pages (with reference
counts), unresolved contradictions, thin pages (one source), seeds, and recent journal ideas, plus the owner's
current focus from `90-system/about.md`. Don't re-scan by hand what the script covers.

If the owner named a topic ("gaps on pricing"), keep only signals related to it. With qmd, widen with
`qmd query $'intent: gaps and open questions about <topic>\nvec: <topic> unknowns' -c wiki -c outputs`.

## 2. Cluster and rank
1. **Cluster**: merge signals that point at the same missing knowledge (a wanted page plus an open question plus a
   query gap about the same thing are one gap). Name each cluster as a question.
2. **Score** each cluster (high/med/low) on:
   - **Focus fit**: does it serve the current focus or an active project? (weighs most)
   - **Leverage**: how many pages/answers would improve (reference counts, thin `stable` pages, contradictions
     blocking conclusions)
   - **Cost**: is one good source likely to close it?
3. Keep the **top 5-7**. Drop the rest into a one-line "also noticed" list.

## 3. Propose sources
For each top gap, suggest **how to close it**:
- The kind of source that would settle it (primary paper, official docs, a practitioner's write-up, data, an
  interview), and 1-2 concrete search queries.
- If web search tools are available and the owner wants it, find 2-3 candidate URLs per gap and label them by
  type and credibility. **Don't capture anything yet.**
- Gaps the owner can answer themselves ("what's my take on X?") get a note: "answer in your journal or tell me".

## 4. Save and log
Write `50-outputs/queries/YYYY-MM-DD-gaps.md` (`type: query`):
```markdown
# Knowledge gaps: YYYY-MM-DD

**Focus:** <from about.md>

| # | Gap (as a question) | Evidence | Why it matters | How to close it |
|---|---|---|---|---|
| 1 | … | [[page-a]] open question, [[query-x]] gap, [[wanted-page]] ×3 | unblocks … | primary source on …; search: "…" |

## Candidate sources (if searched)
- Gap 1: [title](url): type, credibility note

## Also noticed
- …
```
Append to `log.md`: `## [YYYY-MM-DD] gaps | top: <gap 1>, <gap 2>` + `- saved: …`. Run `scripts/qmd-sync.sh`.

## 5. Hand off
Ask which gaps to act on, then:
- URLs → `capture` (then `ingest`, one at a time).
- Owner's own answers → they write in the journal; pick them up in `brain-review`.
- Wanted pages that existing sources already cover → offer a `repair`-style fix (create the page from
  what's in the wiki, cited).

## Hard constraints
- Read-only on the wiki. The only writes are the gaps report and the log line.
- Never capture or ingest without the owner choosing the gap and the source.
- Don't invent sources. Candidate URLs must come from an actual search or the owner.
