---
name: ingest
description: Process sources from the second brain inbox (00-inbox/) into the wiki. Archive the original to 10-raw/, write a source summary page, update every concept/entity page it touches with bidirectional links, then update index.md and log.md. Use when the owner says "ingest", "process the inbox", "file this", "compile this source", or drops a file and asks to add it to the brain.
---

# Ingest: 00-inbox/ → 10-raw/ + 20-wiki/

The most important operation. A wrong page written today is a wrong answer in every query for months,
so check in before writing. Rules and page format: `AGENTS.md` §3 and §6.

## 0. Prepare
- Session-start reading done? (`90-system/about.md`, `index.md`, tail of `log.md`.) If not, do it now.
- List the inbox: `ls -1 00-inbox/ | grep -v .gitkeep`. If several items are waiting and the owner didn't name
  one, list them with a one-line guess at each and ask which to start with (default: oldest first).
- **One source at a time.** For a batch request, still finish each source's full cycle before the next.
- Check the owner's check-in preference in `about.md` ("always" / "only for big sources" / "auto").

## 1. Read
- Read the whole source. For PDFs, read every page; for long sources, read in chunks and take notes as you go.
- Images: read the text first, then view only the images that carry information.
- Note: claims, numbers, named people/orgs/tools, definitions, dates, and the author's caveats.

## 2. Map against the wiki
- From `index.md`, list candidate existing pages. For each key concept/entity, search before deciding
  "new page": `grep -ril "<term>" 20-wiki/` and check `aliases:` in frontmatter.
- Classify each touched page: **update** (adds info), **contradicts** (conflicts with an existing claim),
  **create** (no page exists and the topic matters beyond this one source), or **skip**.
- New pages: create as `status: seed` when the source only mentions the topic in passing.
- Look for state changes: does this source supersede a current fact somewhere (role, version, price, plan)?

## 3. Check in (unless the owner set "auto")
Present this and wait:
```
Source: <title> (<type>, <author>, <date>)
Takeaways: 1) … 2) … 3) …
Update:  [[page-a]] (adds X) · [[page-b]] (new data on Y)
Conflict: [[page-c]] says P, source says Q. I'll add a ## Contradictions section
Create:  [[new-concept]] (seed) · [[person-z]] (entity)
Skip:    <what you're leaving out and why>
```
Apply the owner's corrections to the plan. If they say the source is out of scope: skip to step 4, then write a
source page with `status: deprecated` and a one-line reason. Nothing is deleted.

## 4. Archive the original
- Target: `10-raw/YYYY-MM-DD-short-title.<ext>` (date = **today**, the ingest date).
- Attachments first: move them to `10-raw/assets/` and fix their relative paths **while the file is still in
  `00-inbox/`**. Once a file is in `10-raw/` it is immutable.
- Then `mv -n "00-inbox/<file>" "10-raw/<new-name>"` (`-n` = never overwrite). If the name is taken, add `-2`.

## 5. Write the wiki
1. **Source page** `20-wiki/sources/<short-title>.md` from `90-system/templates/source.md`.
   Set `raw:` to the archived path. Fill "What this changes in the wiki" as you go.
2. **For each page in the plan** (read it before editing):
   - Update the top summary if understanding changed.
   - Add facts under the right section with the source cited: `… ([[source-page]])`.
   - Replace **state** facts in place with a new `(as of YYYY-MM-DD)`. Append **events**. Remove nothing the source
     doesn't actually supersede.
   - Conflicts → a `## Contradictions` section: both claims, both sources, no silent merge.
   - Add `[[source-page]]` to the frontmatter `sources:` list, bump `updated:`, and move `seed` → `growing` when it
     now has real content from 2+ sources.
   - Add the link both ways: page ↔ source page, page ↔ related pages.
3. **New pages** from `90-system/templates/concept.md` / `entity.md`: full frontmatter, summary, at least one
   inbound link from an existing page.
4. Typical scale: a substantial source touches 5-15 pages. If it touched fewer than 3, say why in the report.

## 6. Bookkeep
- `index.md`: add new pages under the right section (`- [[page]]: one-line summary (status, N sources)`);
  refresh summaries/source counts for pages that changed meaningfully.
- `log.md` (append at the bottom):
  ```
  ## [YYYY-MM-DD] ingest | <Source Title>
  - created: [[a]], [[b]] · updated: [[c]], [[d]] · raw: 10-raw/YYYY-MM-DD-title.ext
  ```

## 7. Self-check, then report
Run `python3 scripts/lint.py` and fix any **errors** you introduced (broken links, missing index lines, bad
frontmatter). Pre-existing issues: mention them, don't fix them now.

Report to the owner:
- Pages created / updated (as links), contradictions found, open questions raised.
- Suggested next: related sources to find, a question worth asking with `query`.
- Suggest a commit: `git add -A && git commit -m "ingest: <title>"`.

## Hard constraints
- Never edit anything already in `10-raw/` or `40-journal/`. Never delete pages.
- No claim without a source page citation. Mark your own inferences "(inference)".
- Keep the author's caveats and uncertainty. Don't round them away.
