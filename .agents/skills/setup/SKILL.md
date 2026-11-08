---
name: setup
description: Set up or refresh the second brain for its owner. Interview them (or read a pasted bio/assessment) to fill 90-system/about.md, check git, Obsidian and optional tools, and walk through the first ingest. Use when the owner says "set up my profile", "set up the vault", "onboard me", "update my profile", after a role change, or when 90-system/about.md is still empty.
---

# Setup: profile + first run

## 1. Profile (`90-system/about.md`)
- If the owner pastes a bio, CV, or assessment (Gallup, DISC, MBTI, etc.), extract from it first, then ask only
  about what's missing.
- Otherwise interview **one section at a time**, following the headings in `about.md`:
  Who I am · What this vault is for · How I want to work with the agent · Current focus.
  Keep questions short; offer examples; accept "skip".
- Must capture: language & tone, ingest check-in level (`always` / `only for big sources` / `auto`),
  always-do and never-do rules, current focus with an as-of date.
- **Re-run** (profile exists): show the current profile in 5 lines, ask what changed, and update only that.
  Bump `updated:`.
- `90-system/` needs explicit OK: show the final profile and write it on "yes".

## 2. Environment check (report, don't change system settings)
- `git status`: is it a repo? If not, offer `git init`.
- `python3 --version` (the linter needs 3.8+), and run `python3 scripts/lint.py` once.
- Optional tools: `yt-dlp` (video capture), `qmd` (search at scale). Mention, don't install unasked.
- Obsidian (optional): suggest *Open folder as vault*, Templates folder = `90-system/templates`,
  Attachment folder = `10-raw/assets`, Web Clipper saving into `00-inbox/`.

## 3. First run (offer)
"Drop 1-3 articles on one topic into `00-inbox/` (or give me URLs and I'll capture them), and I'll ingest
the first one with you." Then follow the `capture` / `ingest` skills.

## 4. Log
`## [YYYY-MM-DD] setup | profile created` (or `profile updated: <sections>`).
