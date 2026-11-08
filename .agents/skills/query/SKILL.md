---
name: query
description: Answer a question from the second brain wiki with [[wikilink]] citations and a required Gaps section, save substantial answers to 50-outputs/queries/, and offer to file new insight back into the wiki. Use when the owner asks "what do I know about X", "what does my brain say about", "compare X and Y", "summarize my notes on", asks any question that the vault might answer, or says "file that back".
---

# Query: ask the wiki

The wiki is the first source, not the raw files and not your general knowledge. Rules: `AGENTS.md` §3, §6.

## 1. Find
1. Read `index.md`; pick candidate pages by title/summary.
2. Widen with search: `grep -ril "<term>\|<synonym>" 20-wiki/ 30-projects/` (and `qmd` if installed).
3. Read the candidates fully, then follow `## Related` links one hop if they look relevant.
4. Only if the wiki is thin: check `10-raw/` sources directly, and say you did ("the wiki doesn't cover this
   yet; from the raw source …"). That gap is itself a finding: suggest ingesting/re-ingesting.

## 2. Answer
- Lead with the direct answer, then the support.
- Cite inline as `[[page-name]]` for every non-obvious claim. Cite source pages for specific numbers/quotes.
- Respect `## Contradictions` sections: present both sides, don't pick silently.
- Mark general knowledge that is *not* from the vault: "(not in vault)". Mark inferences: "(inference)".
- Choose the format that fits: prose, comparison table, timeline, checklist, Mermaid diagram, Marp slides.

## 3. Gaps (required for every substantial answer)
```
## Gaps
- What the wiki could not answer, and what kind of source would fill it.
- Stale or single-source claims the answer relied on.
```
An empty Gaps section is almost always wrong. Look harder.

## 4. Save (if substantial)
Substantial = new synthesis, comparison, decision support, or anything over a few paragraphs.
Skip saving for quick lookups ("when did I ingest X?").
- Write `50-outputs/queries/YYYY-MM-DD-short-title.md` from `90-system/templates/query.md`.
- Append to `log.md`: `## [YYYY-MM-DD] query | <question, shortened>` with a `- saved: 50-outputs/queries/…` line.

## 5. Offer to file back
End with one line: "Want me to file this back?", with a concrete proposal:
- A new `20-wiki/syntheses/<name>.md` page (template `synthesis.md`), **or**
- Specific additions to existing pages (name them).

On "yes": write it like an ingest (citations, `sources:`, bidirectional links, `index.md`, `log.md` entry
`## [YYYY-MM-DD] query | filed back: <title>`), and set `filed_back: true` in the saved query file.
Synthesis pages cite the wiki source pages behind them, not the query file.

## Hard constraints
- Never present general knowledge as if it came from the vault.
- Never edit wiki pages during the answer itself; changes only happen through file-back, with the owner's yes.
