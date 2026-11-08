---
name: second-brain
description: Entry point and router for any request about the second brain vault. Work out what the owner wants and run the right flow (capture, ingest, query, lint, repair, project, brain-review, setup), chaining several when needed. Use when a request is vague or spans several steps ("deal with my inbox", "add this and tell me how it fits", "what should I do next?", "help me with my notes", "/second-brain"), when it's unclear which flow applies, or at the start of a session in this vault.
---

# Second Brain: router

You don't do the work here. You **decide which flow runs, in what order**, and then follow that flow's
`SKILL.md` exactly. Rules live in `AGENTS.md`; procedures live in `.agents/skills/<flow>/SKILL.md`.

## 1. Orient (cheap, every time)
1. If you haven't done it this session, do the session-start reading: `90-system/about.md`, `index.md`, and the
   tail of `log.md` (`grep "^## \[" log.md | tail -10`).
2. Snapshot the vault state (one command; no page reads):
   ```bash
   echo "inbox: $(find 00-inbox -type f ! -name .gitkeep | wc -l)"; \
   echo "last lint: $(grep '^## \[.*\] lint' log.md | tail -1)"; \
   echo "last review: $(grep '^## \[.*\] review' log.md | tail -1)"; \
   echo "indexed pages: $(grep -c '^- \[\[' index.md)"; \
   grep -q '^- Role / work: *$' 90-system/about.md && echo "profile: EMPTY" || echo "profile: ok"
   ```

## 2. Classify the request
Match on **intent, not keywords**. Pick the first row that fits.

| The owner wants to… | Signals | Flow |
|---|---|---|
| Set up or change how the brain knows them | "set up", "onboard", "update my profile", role change; or **profile EMPTY** and the request isn't urgent | `setup` |
| Keep something for later | URL, pasted text/transcript/idea, "save", "clip", "remember this" (with no "process" or "add to wiki") | `capture` |
| Turn material into knowledge | "ingest", "process", "file this", "add to my brain/wiki", a path in `00-inbox/` | `ingest` |
| Learn something from the vault | a question; "what do I know", "compare", "summarize my notes", "why did we…" | `query` |
| Keep a good answer | "file that back", "save this as a page" (right after a query) | `query` §5 (file-back) |
| Know if the vault is healthy | "lint", "check", "audit", "what's broken", "clean up" (no specific item) | `lint` |
| Fix specific problems | "fix 1-3", "merge X and Y", "fix broken links", approves lint items | `repair` |
| Work on a project | project name from `index.md` › Projects, "start/update/close project", "where are we on X", "log what we did" | `project` |
| Step back | "review", "what's on my plate", "what did I miss", "plan my week", "process my journal" | `brain-review` |
| Nothing specific | "what should I do?", "help with my brain", bare `/second-brain` | §4 Suggest |

**Ambiguous?** Ask **one** short question with the 2 most likely flows as options, e.g.
"Save it to the inbox for later, or ingest it into the wiki now?" Don't ask when the default below applies.

Defaults when unsure:
- URL or pasted content with no verb → `capture`, then offer ingest.
- A question that the vault clearly doesn't cover (nothing in `index.md`) → say so in one line and answer as `query`
  with a large Gaps section. Offer to `capture` sources on it.
- "Clean up" with a lint report less than 7 days old → `repair` proposal from that report; otherwise `lint`.

## 3. Chain flows (multi-step requests)
Split compound requests into flows and run them **in sequence, each to completion** (including its own
check-ins and log entry) before starting the next. Announce the chain first in one line:
"Plan: capture → ingest → query. Starting with capture."

Common chains:
| Request | Chain |
|---|---|
| "Add this article and tell me how it fits" | `capture` → `ingest` → `query` ("how does X relate to what I know?") |
| "Process my inbox" (N items) | `ingest` × N, one at a time, oldest first, a check-in per source unless `auto` |
| "Clean up the vault" | `lint` → (owner picks items) → `repair` |
| "Weekly maintenance" | `brain-review` → `lint` → then offer `ingest` for the inbox |
| "Research X for project Y" | `query` → file-back → `project` update (link the synthesis in the project log) |
| "Start project X based on my notes" | `query` (context on X) → `project` start (pre-fill the brief, then interview) |

Chaining rules:
- **Stop at every owner decision point** (ingest check-in, lint → repair, file-back, brief edits). Never treat the
  chain's announcement as approval for the gated steps.
- If a step fails or is blocked, stop the chain, report where you stopped and why, and
  offer to resume.
- More than 5 inbox items or more than 3 flows: confirm scope first ("12 items in the inbox. Do all, or the 3 oldest?").

## 4. Suggest (when there's no clear request)
Use the snapshot from §1 and propose **the top 1-3** actions, highest first:
1. Profile EMPTY → `setup`.
2. Inbox has items → `ingest` (name the oldest 1-3 with their age).
3. Last lint more than 30 days ago (or never, and the index has 10+ pages) → `lint`.
4. Last review more than 7 days ago → `brain-review`.
5. Active project with no log entry for more than 14 days → `project` resume.
6. Otherwise → suggest a `query` on the current focus from `about.md`, or capturing sources for its open questions.

Present them as a short numbered list and ask which to run.

## 5. Hand off
1. Read `.agents/skills/<flow>/SKILL.md` in full (or invoke the skill by name if your tool supports it).
2. Follow it exactly: its steps, check-ins, self-check, and hard constraints override anything here.
3. When a flow finishes, either continue the announced chain or end with **one** suggested next step
   (e.g. after ingest: "Ask a question across these sources?"; after lint: "Say *fix 1-3*").

## Hard constraints
- The router itself writes nothing except through a flow. No direct wiki edits "on the way".
- One flow at a time; every flow logs its own entry. The router adds no extra log lines.
- `AGENTS.md` §6 hard rules apply throughout.
