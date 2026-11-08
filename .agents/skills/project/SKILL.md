---
name: project
description: Start, update, or close a project in the second brain (30-projects/<name>/ with brief.md and an append-only log.md). Use when the owner says "start a project", "new project", "update project X", "log what we did on X", "where are we on X", "pick up project X", or "close/archive project X".
---

# Project: start · update · resume · close

A project folder lets any agent join cold. `brief.md` = what it was supposed to be (intent, owner approves
changes). `log.md` = what it became (append-only). Detect the mode from the request; ask if unclear.

## Start
1. Name: kebab-case folder `30-projects/<name>/`. Check `index.md` that it doesn't exist already.
2. Interview the owner **one section at a time**, following `90-system/templates/project-brief.md`:
   Why · Outcome · Who it's for · Scope in/out · Constraints & rules · Open questions.
   - Push back **once** per section on vague answers: "everyone" is not a segment, "more engagement" is not an
     outcome, "ASAP" is not a deadline. Offer a sharper rewording.
   - "I don't know" is valid → record it under Open questions as `- [ ]`.
   - Pull relevant context from the wiki and link it under Key links.
3. Write `brief.md` and `log.md` (from `project-log.md`, first entry `start`).
4. Add to `index.md` under Projects: `- [[30-projects/<name>/brief|<Name>]]: one-line outcome (active)`.
5. `log.md` (root): `## [YYYY-MM-DD] project | start <name>`.

## Update (after meaningful work)
1. Read `brief.md` and the tail of the project's `log.md`.
2. Append to the project log:
   ```
   ## [YYYY-MM-DD] <short label>
   - What happened:
   - Decisions: (with why)
   - Artefacts: [[…]] (files saved in the project folder)
   - Next:
   ```
3. Save produced artefacts in the project folder (drafts, specs, analyses).
4. If scope/outcome changed, **propose** a brief edit; apply only on the owner's OK.
5. Knowledge that outlives the project (lessons, facts about people/tools) → file into `20-wiki/` with citations
   (the project log counts as a source; link it).
6. Refresh the project's line in `index.md` (status, one-line state). Root `log.md`: `## [YYYY-MM-DD] project | update <name>`.

The log and index entry decay first because they feel invisible. Don't skip them.

## Resume ("where are we on X?")
Read `brief.md` + the last ~5 log entries + linked artefacts, then answer: goal, current state, last decision,
open questions, suggested next step. Read-only unless the owner asks for changes.

## Close
1. Set `status: archived` in `brief.md`.
2. Append a final `retrospective` entry: outcome vs. intent, what worked, what didn't, lessons.
3. File lessons into the wiki (concept pages or a synthesis) with links back to the project.
4. Update `index.md` (status archived) and root `log.md`: `## [YYYY-MM-DD] project | close <name>`.

## Hard constraints
- Project `log.md` is append-only. Never rewrite past entries; correct with a new entry.
- `brief.md` changes need the owner's approval.
