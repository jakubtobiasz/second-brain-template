#!/usr/bin/env python3
"""Collect knowledge-gap signals from the vault (mechanical part of the gap-finder skill).

It reads, never writes. The agent ranks the signals and turns them into a reading list.

Usage:
    python3 scripts/gaps.py            # markdown summary
    python3 scripts/gaps.py --json     # machine-readable

Signals:
    open-question   unchecked/bulleted items under "## Open questions" in wiki and project pages
    query-gap       bullets under "## Gaps" in saved answers (50-outputs/queries/)
    wanted-page     [[links]] to pages that don't exist, by number of referencing pages
    thin-page       growing/stable pages backed by a single source
    seed            seed pages (stubs waiting for material)
    contradiction   pages with an unresolved "## Contradictions" section
    journal-idea    items under "## Ideas" in recent journal entries (last 30 days)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint  # noqa: E402  (reuse the parser and vault walker)

ROOT = lint.ROOT
JOURNAL_DAYS = 30
PLACEHOLDER = re.compile(r"^(\s*-\s*(\[ \]\s*)?)?(…|\.\.\.)?\s*$")


def section_items(body: str, heading: str):
    """Bullet items under a '## heading' (until the next '## ')."""
    text = lint.COMMENT_RE.sub("", body)
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    if not m:
        return []
    items = []
    for line in m.group(1).splitlines():
        s = line.strip()
        if not s.startswith(("-", "*")) or PLACEHOLDER.match(s):
            continue
        if s.startswith(("- [x]", "- [X]")):
            continue  # answered
        items.append(re.sub(r"^[-*]\s*(\[ \]\s*)?", "", s))
    return items


def collect(today: dt.date):
    signals = defaultdict(list)
    resolver = lint.build_resolver()
    wanted = defaultdict(set)

    pages = []
    for d in ("20-wiki", "30-projects", "40-journal", "50-outputs/queries"):
        base = ROOT / d
        if base.exists():
            pages += [lint.Page(p) for p in lint.iter_md(base)]

    for p in pages:
        fm = p.fm or {}
        body = p.body if p.fm is not None else p.text
        for t in p.links:
            if lint.resolve(t, resolver) is None:
                wanted[t].add(p.rel)

        if p.rel.startswith(("20-wiki/", "30-projects/")):
            for q in section_items(body, "Open questions"):
                signals["open-question"].append({"page": p.rel, "text": q})
            m = re.search(r"^##\s+Contradictions\s*$(.*?)(?=^##\s|\Z)", lint.COMMENT_RE.sub("", body), re.M | re.S | re.I)
            if m and re.search(r"\w", m.group(1)):
                signals["contradiction"].append({"page": p.rel, "text": fm.get("title", p.stem)})

        if p.rel.startswith("20-wiki/"):
            status = str(fm.get("status", ""))
            srcs = fm.get("sources") or []
            srcs = srcs if isinstance(srcs, list) else [srcs]
            if status == "seed":
                signals["seed"].append({"page": p.rel, "text": fm.get("title", p.stem),
                                        "created": fm.get("created", "")})
            elif status in ("growing", "stable") and len(srcs) == 1 and fm.get("type") != "source":
                signals["thin-page"].append({"page": p.rel, "text": fm.get("title", p.stem), "source": srcs[0]})

        if p.rel.startswith("50-outputs/queries/"):
            for g in section_items(body, "Gaps"):
                signals["query-gap"].append({"page": p.rel, "text": g})

        if p.rel.startswith("40-journal/"):
            d = lint.parse_date(p.stem)
            if d and (today - d).days <= JOURNAL_DAYS:
                for idea in section_items(body, "Ideas"):
                    signals["journal-idea"].append({"page": p.rel, "text": idea})

    for t, refs in sorted(wanted.items(), key=lambda x: (-len(x[1]), x[0])):
        signals["wanted-page"].append({"page": ", ".join(sorted(refs)), "text": t, "count": len(refs)})

    focus = []
    about = ROOT / "90-system" / "about.md"
    if about.exists():
        _, body, _ = lint.parse_frontmatter(about.read_text(encoding="utf-8"))
        m = re.search(r"^##\s+Current focus.*?$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
        if m:
            focus = [s.strip("- ").strip() for s in m.group(1).splitlines() if s.strip("- ").strip()]
    return signals, focus


ORDER = ["query-gap", "open-question", "wanted-page", "contradiction", "thin-page", "seed", "journal-idea"]
TITLES = {
    "query-gap": "Gaps from saved answers", "open-question": "Open questions",
    "wanted-page": "Wanted pages (linked, missing)", "contradiction": "Unresolved contradictions",
    "thin-page": "Thin pages (single source)", "seed": "Seed pages", "journal-idea": "Recent journal ideas",
}


def to_markdown(signals, focus):
    out = ["# Gap signals", ""]
    out.append("**Current focus:** " + ("; ".join(focus) if focus else "_not set in 90-system/about.md_"))
    out.append("")
    out.append("**Counts:** " + " · ".join(f"{k} {len(signals.get(k, []))}" for k in ORDER))
    out.append("")
    for k in ORDER:
        items = signals.get(k, [])
        if not items:
            continue
        out.append(f"## {TITLES[k]} ({len(items)})")
        for it in items[:40]:
            extra = f" ×{it['count']}" if "count" in it else ""
            out.append(f"- {it['text']}{extra} (`{it['page']}`)")
        if len(items) > 40:
            out.append(f"- … {len(items) - 40} more")
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = ap.parse_args(argv)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    signals, focus = collect(today)
    if args.json:
        print(json.dumps({"focus": focus, **{k: signals.get(k, []) for k in ORDER}}, indent=2))
    else:
        print(to_markdown(signals, focus))
    return 0


if __name__ == "__main__":
    sys.exit(main())
