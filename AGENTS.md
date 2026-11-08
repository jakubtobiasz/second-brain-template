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
├── .agents/skills/      # operation procedures (second-brain router + capture, ingest, query, …)
└── .claude/skills       # symlink -> ../.agents/skills (for Claude Code)
```

| Location | Owner writes | Agent writes | Notes |
|---|---|---|---|
| `00-inbox/` | yes | only to add captures on request | Agent moves files **out** during ingest |
| `10-raw/` | add only | **never edit or delete** | Immutable. Corrections arrive as new sources |
| `20-wiki/` | rarely | yes | Agent-owned. Owner edits are respected and never overwritten silently |
| `30-projects/` | yes | yes | `brief.md` = intent (owner approves changes); `log.md` = append-only |
| `40-journal/` | yes | **no** (read-only) | Agent may *link to* and *extract from* journal entries, never rewrite them |
| `50-outputs/` | — | yes | Agent writes; owner reviews |
| `90-system/`, `.agents/skills/` | yes | only with explicit OK | Profile, templates, and procedures change rarely and deliberately |
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

The owner triggers operations in plain language. When it's unclear which flow applies, or the request spans
several, start with the `second-brain` router skill. Each operation has a **skill** with the full procedure in
`.agents/skills/<name>/SKILL.md` (also reachable as `.claude/skills/` through a symlink). Load the skill when its
flow starts. The summaries below are the contract; the skills are the step-by-step.

| Skill | Trigger (examples) | What it does |
|---|---|---|
| `second-brain` | vague or multi-step requests, "what should I do?" | **Router**: classifies the request, chains flows in order, suggests next actions from vault state. Writes nothing itself |
| `capture` | "save this", "clip this URL" | Verbatim copy into `00-inbox/` with metadata. No wiki changes |
| `ingest` | "ingest", "process the inbox" | One source at a time: read → map → **check in** → archive to `10-raw/` → source page + updates to 5-15 pages with links both ways → index + log |
| `query` | "what do I know about X?" | Index first → answer with `[[citations]]` + required **Gaps** → save if substantial → offer to file back into the wiki |
| `lint` | "check vault health" | `scripts/lint.py --write` + semantic review → ranked report in `50-outputs/lint/`. **Report only** |
| `repair` | "fix 1-3" | Applies owner-approved lint items one at a time, re-lints, logs |
| `project` | "start / update / close project X" | `30-projects/<name>/brief.md` (intent, owner approves edits) + append-only `log.md` |
| `brain-review` | "weekly review" | Reads journal, log, inbox, projects → proposes promotions, open loops, focus. Applies nothing |
| `setup` | "set up my profile" | Interviews the owner into `90-system/about.md`, checks the environment, guides the first ingest |

### Contracts every skill honours
- **Capture is free-form.** The owner drops anything in `00-inbox/`. It is the only place without discipline.
- **Ingest checks in before writing** (unless `about.md` says `auto`), processes **one source at a time**, and never
  leaves a page without citations, index line, or back-links.
- **Query never presents general knowledge as vault knowledge**, always ends with Gaps, and changes the wiki only
  through an approved file-back.
- **Lint never fixes.** Repair only touches approved items.
- **Projects**: brief = what it was supposed to be; log = what it became. Lasting knowledge gets filed into `20-wiki/`.
- **Reviews propose**; the owner decides. `40-journal/` is never edited.

### Corrections and rule changes
When the owner corrects you ("no, that's wrong", "always do X"), fix the content, then propose a one-line
addition to **§7 Learned conventions** below. Keep that list short. Merge or prune instead of growing it.
If a correction concerns a procedure, propose an edit to that skill's `SKILL.md` instead.

### Adding a skill
Create `.agents/skills/<name>/SKILL.md` (frontmatter `name` + a `description` saying *when* to use it), add a row
to the table above, and log it as `schema`. `.claude/skills` is a symlink to that folder, so there is nothing to copy.

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

**Enforcement.** Rules 1-2 rely on you. The linter's `raw-modified` check (git) catches edits to
`10-raw/` after the fact.

Version control: the vault is a git repo. Suggest a commit after each operation
(`ingest: <title>`, `lint: 2026-01-15`) so every change is reviewable with `git diff`.

---

## 7. Learned conventions

<!-- Owner-approved rules discovered while using this vault. Keep ≤ 10. Newest last. -->

- _(empty: add rules here as you co-evolve the system)_
