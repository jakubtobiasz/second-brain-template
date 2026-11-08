---
type: reference
title: Prior art & lessons
updated: 2026-11-08
---

# Prior art & lessons

Research done 2026-11-08 (Exa, ~100 sources reviewed). Used to design `AGENTS.md`.

## Similar projects

| Project | Idea worth stealing |
|---|---|
| [Karpathy, LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | The original pattern: raw → wiki → schema; ingest / query / lint; index.md + log.md |
| [superhero-tech/super-brain](https://github.com/superhero-tech/super-brain) | Operations as skills; profile in a file (`about.md`); check-in before ingest writes; required **Gaps** section; project layer |
| [olegiv/llm-wiki-go](https://github.com/olegiv/llm-wiki-go) | Deterministic linter in code; `## Contradictions` section instead of silent merges |
| [Laksh-star/claude-llm-wiki](https://github.com/Laksh-star/claude-llm-wiki) | "Bridge" pages between domains; `/wiki:next` gap finder; agent-export context layer |
| [BlaiseMoses01/obsidian-second-brain-starter](https://github.com/BlaiseMoses01/obsidian-second-brain-starter) | Raw immutability enforced via `.claude/settings.json` deny rules |
| [joshpocock/karpathy-obsidian-vault](https://github.com/joshpocock/karpathy-obsidian-vault) | Lint is read-only; fixes approved one by one |
| [ekadetov/llm-wiki](https://github.com/ekadetov/llm-wiki) | Separates "save source" from "compile into wiki"; git commit per compile |
| [Berkay2002/wikillm](https://github.com/Berkay2002/wikillm) | Concept-ownership table before parallel ingest to avoid duplicates |
| [danicollia/dani-brain](https://github.com/danicollia/dani-brain) | PARA layout; per-project knowledge / todo / log trio |
| [Liakhov/second-brain-template](https://github.com/Liakhov/second-brain-template) | `history.md` of user corrections; patterns only after 3+ sources |
| [wikibrain-app/wikibrain](https://github.com/wikibrain-app/wikibrain) | Schema served via MCP; "pending sources" backlog |

## Lessons from practitioners

**What works**
- Schema enforcement + mechanical validation ([Isaza](https://santiagoisaza.com/projects/llm-wiki/)).
- One source at a time; batch ingest yields weak connections ([Monge](https://www.christianmonge.com/blog/karpathy-llm-wiki)).
- Every run starts from disk: index + log tail, do the job, write back ([Veho](https://tech.shipveho.com/posts/i-built-a-second-brain-and-you-should-too/)).
- The payoff is often the agent having *context about you*, not the notes themselves ([Hansen](https://jamalhansen.com/blog/six-months-of-an-llm-maintained-wiki/)).

**Failure modes** (designed against in AGENTS.md)
- Agents append by default, so the same fact ends up in 3 versions and stale "current" state lingers ([Tyloch](https://tyloch.biz/posts/llm-wiki-second-brain-rot/)). → *State vs. events rule.*
- Duplicate entity pages, changelog updated but reference text stale ([Tuszynski](https://www.mpt.solutions/karpathys-llm-wiki-works-heres-what-broke-when-i-ran-it-at-real-scale/)). → *Search before create; update every affected section.*
- "Scatter" (many pages on one topic) and "diary drift" (logs bury current rules) ([Conner](https://medium.com/@shane.conner/my-agents-wiki-was-written-faster-than-it-was-read-and-what-was-read-sold-me-back-debt-i-had-a8085319c68b)). → *One canonical page; summary at top.*
- LLM lint stops being reliable at ~350 pages ([de Assis](https://medium.com/@paulo.deassis/three-months-of-my-llm-wiki-a-follow-up-and-an-update-43d95cc9246b)). → *Prefer scripted checks.*
- Shell `mv` breaks links; caveats dropped on rewrite ([knowtarium](https://knowtarium.com/guides/claude-code-second-brain)). → *git mv + link updates; preserve caveats.*
- Noise: the agent records too much ([Vellum](https://dev.to/vellumkasane/four-things-that-broke-when-i-ran-karpathys-llm-wiki-with-claude-code-and-the-fixes-4h4f)). → *Hard rule 10.*

## Ideas for later
- ~~Script-based linter~~: done (`scripts/lint.py`).
- ~~Hook that blocks writes to `10-raw/` and `40-journal/`~~: done (`.claude/hooks/protect_paths.py`).
- Lock on `index.md` / `log.md` if several agent sessions write in parallel ([Krenin](https://dev.to/krenin88/an-llm-wiki-that-keeps-context-when-the-session-ends-283i)).
- ~~Operations as skills~~: done (`.agents/skills/`, symlinked as `.claude/skills`).
- qmd search once `index.md` gets large.
