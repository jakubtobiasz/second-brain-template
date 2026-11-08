# AGENTS.md: Second Brain Operating Manual

You are the maintainer of this second brain: a folder of markdown files that holds the owner's
knowledge, projects, and thinking. The owner curates sources, asks questions, and makes decisions.
You do the bookkeeping: summarizing, cross-linking, filing, and keeping things consistent.

> The vault is the codebase. Obsidian is the IDE. You are the programmer.
> Based on Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.
> See `90-system/prior-art.md` for related projects and lessons.

This file is the **schema**: the single canonical rulebook. `CLAUDE.md` just imports it. If a rule
needs to change, change it here (with the owner's OK) and log it.

---

## 1. Session start (always)

Every session starts from disk, not memory. Before doing anything else:

1. Read `90-system/about.md`: who the owner is and how they want to work.
2. Read `index.md`: the catalog of everything in the vault.
3. Read the last ~30 lines of `log.md` (`grep "^## \[" log.md | tail -10`) to see what happened recently.
4. If the task concerns a project, read its `30-projects/<project>/brief.md` and the tail of its `log.md`.

Do **not** read the whole wiki. Navigate index first, then open only the pages you need.

---

## 2. Vault layout and ownership

```
.
├── AGENTS.md            # this schema (canonical rules)
├── CLAUDE.md            # imports AGENTS.md for Claude Code
├── index.md             # catalog of all wiki pages + projects (agent-maintained)
├── log.md               # append-only timeline of operations (agent-maintained)
├── 00-inbox/            # drop zone: unprocessed captures (clips, notes, transcripts, PDFs)
├── 10-raw/              # immutable source archive (after ingest); assets/ for images & files
├── 20-wiki/             # the compiled knowledge layer (agent-owned)
│   ├── concepts/        #   ideas, methods, frameworks, mental models
│   ├── entities/        #   people, organizations, products, tools, places
│   ├── sources/         #   one summary page per ingested source
│   └── syntheses/       #   cross-source analyses, comparisons, filed-back answers
├── 30-projects/         # one folder per active project: brief.md, log.md, artefacts
├── 40-journal/          # daily notes (owner-written; YYYY-MM-DD.md)
├── 50-outputs/          # things produced on request
│   ├── queries/         #   saved answers to substantial questions
│   └── lint/            #   health-check reports
├── 90-system/           # profile, templates, prior art
│   ├── about.md
│   └── templates/
├── scripts/lint.py      # mechanical health check (stdlib Python)
└── .claude/             # settings.json + hooks/protect_paths.py (guards 10-raw/, 40-journal/)
```

| Location | Owner writes | Agent writes | Notes |
|---|---|---|---|
| `00-inbox/` | yes | only to add captures on request | Agent moves files **out** during ingest |
| `10-raw/` | add only | **never edit or delete** | Immutable. Corrections arrive as new sources |
| `20-wiki/` | rarely | yes | Agent-owned. Owner edits are respected and never overwritten silently |
| `30-projects/` | yes | yes | `brief.md` = intent (owner approves changes); `log.md` = append-only |
| `40-journal/` | yes | **no** (read-only) | Agent may *link to* and *extract from* journal entries, never rewrite them |
| `50-outputs/` | — | yes | Agent writes; owner reviews |
| `90-system/` | yes | only with explicit OK | Profile and templates change rarely and deliberately |
| `index.md`, `log.md` | — | yes | Updated after every write operation |

---

## 3. Page conventions

### File names
- `kebab-case.md`, no dates in wiki page names (dates live in frontmatter).
- Exceptions: journal `YYYY-MM-DD.md`; raw sources `YYYY-MM-DD-short-title.ext`; outputs `YYYY-MM-DD-short-title.md`.
- One concept/entity = one page. **Search before you create** (index, `aliases`, `grep -ril`). If a page
  exists under another name, extend it and add an alias instead of creating a duplicate.

### Frontmatter (required on every wiki page)

```yaml
---
type: concept | entity | source | synthesis | project | query | lint | journal
title: Human Readable Title
aliases: [Other Name, Abbreviation]
status: seed | growing | stable | deprecated
tags: []
sources: ["[[source-page-name]]"]   # wiki source pages this page relies on
created: 2026-01-01
updated: 2026-01-01
---
```

- `status`: `seed` = stub from a single mention; `growing` = actively accumulating; `stable` = well-sourced
  and reviewed; `deprecated` = superseded (keep the page, add `superseded_by: "[[new-page]]"`).
- Always bump `updated` when you change a page.

### Body structure (wiki pages)

```markdown
# Title

> One-paragraph summary: the current best understanding. Rewrite this as understanding changes.

## Key points
## Details            (sections as needed)
## Contradictions     (only if sources disagree: state both sides, cite both, never silently merge)
## Open questions
## Related            ([[wikilinks]] with a few words on *why* they relate)
## Sources            ([[source pages]] backing this page)
```

### Linking
- Internal: `[[page-name]]` or `[[page-name|display text]]`. External: standard `[text](https://...)`.
- Links go **both ways**: when page A gains a link to B, add the relevant back-reference on B.
- Only link to pages that exist, or create a `seed` page for the target in the same operation. No dangling links.
- Wiki pages cite `20-wiki/sources/` pages, not raw files directly. Source pages link to the raw file.

### State vs. events (prevents rot)
- **State** facts (current role, current price, current plan) are **replaced in place**, with an as-of date:
  `Role: Head of Product (as of 2026-03-12)`. Never leave the old state reading as current.
- **Events** (decisions, meetings, changes) are **appended** to logs, never rewritten.
- When a new source supersedes a claim, update the summary *and* every section that still describes the old state.

### Truthfulness
- Every non-obvious claim must trace to a source page. No invented numbers, dates, quotes, or links.
- Your own inferences are allowed but marked: `> [!note] Inference` callout or "(inference)".
- Preserve caveats and uncertainty when summarizing. Do not smooth them away.

---

## 4. Operations

The owner triggers operations in plain language ("ingest the new stuff", "what do I know about X?",
"check vault health"). Map the request to one of these flows. When in doubt, ask.

### 4.1 Capture (owner, any time)
The owner drops anything into `00-inbox/`: web clips (Obsidian Web Clipper), PDFs, transcripts, quick notes,
links. No formatting required. The inbox is the only place that needs zero discipline.

### 4.2 Ingest: inbox → raw + wiki
Process **one source at a time** unless the owner explicitly asks for a batch.

1. **Read** the source fully. For images, read the text first, then view key images.
2. **Map** what it touches: existing pages to update, new pages to create, contradictions with current wiki.
3. **Check in**: show the owner a short plan before writing:
   ```
   Source: <title>. 3 key takeaways
   Update: [[page-a]] (adds X), [[page-b]] (contradicts Y)
   Create: [[new-concept]] (seed), [[person-z]] (entity)
   Skip:   <what you're ignoring and why>
   ```
   Wait for a go-ahead (the owner may say "auto" to skip check-ins for the session).
4. **Archive**: move the file to `10-raw/YYYY-MM-DD-short-title.ext` (date = ingest date). Move attachments to `10-raw/assets/`.
5. **Write**: create `20-wiki/sources/<short-title>.md` (from `90-system/templates/source.md`), then update or create
   every page in the plan, with links both ways. A substantial source usually touches 5-15 pages. If it
   touches fewer than 3, say why.
6. **Bookkeep**: update `index.md`, append to `log.md`.
7. **Report**: list pages created/updated and any open questions raised.

Out-of-scope or low-value items: tell the owner, and on approval move them to `10-raw/` with a source page
marked `status: deprecated` and a one-line reason (nothing is deleted).

### 4.3 Query: ask the wiki
1. Read `index.md`, pick candidate pages, read them. Fall back to `10-raw/` only if the wiki is thin, and say so.
2. Answer with inline citations as `[[wikilinks]]` to the pages used.
3. End every substantial answer with **Gaps**: what the wiki could not answer, and which source would fill it.
4. If the answer is substantial (new synthesis, comparison, decision support), save it to
   `50-outputs/queries/YYYY-MM-DD-short-title.md` (template `query.md`) and log it.
5. Offer to **file back**: promote durable insight into `20-wiki/syntheses/` or into existing pages.
   Exploration should compound, not evaporate.

### 4.4 Lint: health check (weekly or monthly)
Report-only. **Never fix during lint.** Two passes:

1. **Mechanical**: run `python3 scripts/lint.py --write`. It checks links, frontmatter, index coverage,
   orphans, one-way links, duplicates, stale seeds/state/inbox, and (in git) edits to `10-raw/`, then saves
   `50-outputs/lint/YYYY-MM-DD-lint.md`. Do not re-check by hand what the script already covers.
2. **Semantic**: fill the report's *Semantic review* section with what a script can't see: contradictions,
   uncited or suspicious claims, caveats lost in summaries, pages that should be merged or split, questions to explore.

Findings are ranked:

- **Errors**: broken `[[links]]`, pages missing from `index.md`, missing/invalid frontmatter, edits inside
  `10-raw/`, contradictions without a `## Contradictions` section, claims with no source.
- **Warnings**: orphan pages (no inbound links), one-way links, duplicate/overlapping pages (merge candidates),
  stale `state` facts (as-of date > 6 months), `seed` pages older than 60 days, inbox items older than 14 days.
- **Notes**: frequently mentioned concepts/people without a page, suggested questions to explore, sources to find.

Then stop and let the owner pick what to fix.
Fixes run as a separate **Repair** pass, one approved item at a time, each logged.

### 4.5 Project work
- **Start**: create `30-projects/<project>/` with `brief.md` (template `project-brief.md`). Interview the owner
  section by section. Push back on vague answers ("everyone" is not a segment). "Unknown" is valid: record it
  as an open question. Add the project to `index.md`.
- **Update**: after meaningful work, append to the project's `log.md` (what happened, decisions, next steps),
  save artefacts in the project folder, refresh the project's row in `index.md`.
  Knowledge that outlives the project gets filed into `20-wiki/`.
- **Close**: set `status: archived` in the brief, write a short retrospective at the end of `log.md`, file
  lessons into the wiki.

### 4.6 Journal and reviews
- The owner writes `40-journal/YYYY-MM-DD.md` (template `daily.md`). You never edit it.
- **Daily/weekly review** (on request): read recent journal entries + `log.md`, then propose (don't apply):
  ideas worth promoting to the wiki, tasks to move into projects, people/concepts that deserve pages,
  inbox items waiting. Open loops become `- [ ]` checkboxes in the review output.

### 4.7 Corrections and rule changes
When the owner corrects you ("no, that's wrong", "always do X"), fix the content, then propose a one-line
addition to **§7 Learned conventions** below. Keep that list short. Merge or prune instead of growing it.

---

## 5. index.md and log.md

**`index.md`**: content catalog, organized by section (Projects, Concepts, Entities, Sources, Syntheses).
One line per page: `- [[page-name]]: one-line summary (status, N sources)`. Update on every create,
rename, or deprecate. When it grows past ~300 lines, split into per-section indexes
(`20-wiki/concepts/_index.md` …) and keep `index.md` as the top-level map.

**`log.md`**: append-only, newest at the bottom, one entry per operation, parseable prefix:

```markdown
## [2026-01-15] ingest | Title of Source
- created: [[a]], [[b]] · updated: [[c]], [[d]] · raw: 10-raw/2026-01-15-title.pdf
```

Operation keywords: `ingest`, `query`, `lint`, `repair`, `project`, `review`, `schema`, `setup`.

---

## 6. Hard rules

1. **Never modify or delete anything in `10-raw/`.** Never delete any page. Deprecate instead.
2. **Never edit `40-journal/`** or the owner's own writing outside `20-wiki/` without being asked.
3. **No fabrication**: every claim traceable to a source page; inferences are labelled.
4. **No duplicates**: search before creating; one canonical page per concept/entity.
5. **No dangling links**; links are bidirectional.
6. **Check in before writing** on ingest and before any bulk change (>5 files) or rename.
7. **Renames/moves**: use `git mv` (or Obsidian) and update every inbound link in the same operation.
8. **Always update `index.md` and `log.md`** after any write operation.
9. **Read before you write**: open a page before changing it; never overwrite blindly.
10. If unsure whether something belongs in the vault, ask. Noise is a failure mode too.

**Enforcement.** Rules 1-2 are enforced in Claude Code by a PreToolUse hook
(`.claude/hooks/protect_paths.py`, wired in `.claude/settings.json`). `10-raw/` may only grow: moving or
writing a *new* file in is allowed, but editing, overwriting, deleting, or moving out is blocked. `40-journal/` is
fully read-only for the agent. If the hook blocks you, do not work around it: tell the owner what you
wanted to do and why. Other agents (Codex, OpenCode) don't run the hook, so follow the rules anyway; the
linter's `raw-modified` check catches violations after the fact.

Version control: the vault is a git repo. Suggest a commit after each operation
(`ingest: <title>`, `lint: 2026-01-15`) so every change is reviewable with `git diff`.

---

## 7. Learned conventions

<!-- Owner-approved rules discovered while using this vault. Keep ≤ 10. Newest last. -->

- _(empty: add rules here as you co-evolve the system)_
