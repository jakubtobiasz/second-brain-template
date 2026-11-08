#!/usr/bin/env python3
"""Deterministic health check for the Second Brain vault.

Report-only: it never modifies wiki pages. See .agents/skills/lint/SKILL.md.

Usage:
    python3 scripts/lint.py            # print report to stdout
    python3 scripts/lint.py --write    # also save 50-outputs/lint/YYYY-MM-DD-lint.md
    python3 scripts/lint.py --json     # machine-readable findings

Exit code: 1 if any errors were found, else 0.
Python 3.8+ standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIKI = "20-wiki"
INBOX = "00-inbox"
RAW = "10-raw"
LINT_DIR = "50-outputs/lint"  # lint reports quote broken links; never scan them
# Folders whose markdown is scanned for links. Root files index.md / log.md are added explicitly.
SCAN_DIRS = [WIKI, "30-projects", "40-journal", "50-outputs"]
SKIP_PARTS = {".git", ".obsidian", ".trash", "node_modules", ".claude", ".agents"}

TYPE_BY_FOLDER = {
    "concepts": "concept",
    "entities": "entity",
    "sources": "source",
    "syntheses": "synthesis",
}
VALID_TYPES = {"concept", "entity", "source", "synthesis", "project", "query", "lint", "journal", "index", "log"}
VALID_STATUS = {"seed", "growing", "stable", "deprecated"}
REQUIRED_WIKI_FIELDS = ["type", "title", "status", "created", "updated"]
NEEDS_SOURCES = {"concept", "entity", "synthesis"}

STALE_SEED_DAYS = 60
STALE_STATE_DAYS = 180
STALE_INBOX_DAYS = 14

WIKILINK_RE = re.compile(r"(!?)\[\[([^\[\]\n]+?)\]\]")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
AS_OF_RE = re.compile(r"\(as of (\d{4}-\d{2}-\d{2})\)", re.I)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --------------------------------------------------------------------------- parsing

def parse_frontmatter(text: str):
    """Return (dict | None, body, error | None). Minimal YAML subset: scalars and [lists]."""
    if not text.startswith("---"):
        return None, text, None
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text, "frontmatter not closed with ---"
    data: dict = {}
    key = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")) and raw.strip().startswith("- ") and key:
            data.setdefault(key, [])
            if isinstance(data[key], list):
                data[key].append(_scalar(raw.strip()[2:]))
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not m:
            return None, text, f"cannot parse frontmatter line: {raw!r}"
        key, val = m.group(1), m.group(2).strip()
        val = re.sub(r"\s+#.*$", "", val) if not val.startswith(("'", '"')) else val
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [_scalar(x) for x in _split_list(inner)] if inner else []
        elif val == "":
            data[key] = []  # may be a block list that follows
        else:
            data[key] = _scalar(val)
    for k, v in list(data.items()):
        if v == []:
            data[k] = [] if k in ("aliases", "tags", "sources") else ""
    body = "\n".join(lines[end + 1:])
    return data, body, None


def _split_list(s: str):
    out, buf, depth, quote = [], "", 0, None
    for ch in s:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(buf.strip())
            buf = ""
            continue
        buf += ch
    if buf.strip():
        out.append(buf.strip())
    return out


def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def strip_code(text: str) -> str:
    text = FENCE_RE.sub("", text)
    text = COMMENT_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def extract_links(text: str):
    """Yield link targets (without alias/heading/block parts)."""
    for m in WIKILINK_RE.finditer(strip_code(text)):
        target = m.group(2).split("|", 1)[0].split("#", 1)[0].split("^", 1)[0].strip()
        if target and target not in ("...", "…"):
            yield target


def parse_date(v):
    if isinstance(v, str) and DATE_RE.match(v.strip()):
        try:
            return dt.date.fromisoformat(v.strip())
        except ValueError:
            return None
    return None


# --------------------------------------------------------------------------- vault model

class Page:
    def __init__(self, path: Path):
        self.path = path
        self.rel = path.relative_to(ROOT).as_posix()
        self.stem = path.stem
        self.text = path.read_text(encoding="utf-8", errors="replace")
        self.fm, self.body, self.fm_error = parse_frontmatter(self.text)
        self.links = list(extract_links(self.text))

    @property
    def is_wiki(self):
        return self.rel.startswith(WIKI + "/")

    @property
    def is_index_file(self):
        return self.rel == "index.md" or self.stem == "_index"


def iter_md(base: Path):
    for p in base.rglob("*.md"):
        rel = p.relative_to(ROOT)
        if SKIP_PARTS.intersection(rel.parts) or rel.as_posix().startswith(LINT_DIR + "/"):
            continue
        yield p


def build_resolver():
    """Map lowercase basename and lowercase relative path (with/without .md) -> list of rel paths."""
    names = defaultdict(list)
    for p in ROOT.rglob("*"):
        if not p.is_file() or SKIP_PARTS.intersection(p.relative_to(ROOT).parts):
            continue
        rel = p.relative_to(ROOT).as_posix()
        keys = {p.name.lower(), rel.lower()}
        if p.suffix == ".md":
            keys |= {p.stem.lower(), rel[:-3].lower()}
        for k in keys:
            names[k].append(rel)
    return names


def resolve(target: str, resolver):
    t = target.strip().lstrip("/").lower()
    hits = resolver.get(t) or resolver.get(t + ".md")
    return hits[0] if hits else None


# --------------------------------------------------------------------------- checks

class Report:
    def __init__(self):
        self.items = {"error": [], "warning": [], "note": []}

    def add(self, level, check, page, msg, fix=""):
        self.items[level].append({"check": check, "page": page, "message": msg, "fix": fix})


def git_raw_changes():
    """Modified/deleted tracked files under 10-raw (None if not a git repo)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--", RAW],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    bad = []
    for line in out.splitlines():
        code, path = line[:2], line[3:]
        if code.strip() and code != "??" and ("M" in code or "D" in code or "R" in code):
            bad.append((code.strip(), path))
    return bad


def run_checks(today: dt.date) -> tuple[Report, dict]:
    rep = Report()
    resolver = build_resolver()

    files = []
    for d in SCAN_DIRS:
        if (ROOT / d).exists():
            files.extend(iter_md(ROOT / d))
    for f in ("index.md", "log.md"):
        if (ROOT / f).exists():
            files.append(ROOT / f)
    pages = {p.rel: p for p in (Page(f) for f in files)}
    wiki = {r: p for r, p in pages.items() if p.is_wiki and not p.is_index_file}

    # --- inbound link graph
    inbound = defaultdict(set)
    outbound = defaultdict(set)
    for rel, p in pages.items():
        for t in p.links:
            hit = resolve(t, resolver)
            if hit is None:
                rep.add("error", "broken-link", rel, f"[[{t}]] does not resolve",
                        f"create a seed page for '{t}' or fix the link")
                continue
            if hit != rel:
                outbound[rel].add(hit)
                inbound[hit].add(rel)

    # --- index coverage (index.md + any _index.md files reachable from it)
    indexed = set()
    index_pages = [p for p in pages.values() if p.is_index_file]
    for ip in index_pages:
        indexed |= outbound[ip.rel]
    if "index.md" not in pages:
        rep.add("error", "index", "index.md", "index.md is missing")

    # --- per-page checks
    titles = defaultdict(list)
    for rel, p in sorted(wiki.items()):
        if p.fm_error:
            rep.add("error", "frontmatter", rel, p.fm_error)
            continue
        if p.fm is None:
            rep.add("error", "frontmatter", rel, "no YAML frontmatter",
                    "add frontmatter from 90-system/templates")
            continue
        fm = p.fm
        missing = [k for k in REQUIRED_WIKI_FIELDS if not fm.get(k)]
        if missing:
            rep.add("error", "frontmatter", rel, f"missing fields: {', '.join(missing)}")
        ptype = str(fm.get("type", ""))
        if ptype and ptype not in VALID_TYPES:
            rep.add("error", "frontmatter", rel, f"invalid type '{ptype}'")
        folder = rel.split("/")[1] if rel.count("/") >= 2 else ""
        expected = TYPE_BY_FOLDER.get(folder)
        if expected and ptype and ptype != expected:
            rep.add("warning", "type-folder", rel, f"type '{ptype}' but lives in {folder}/ (expected '{expected}')")
        status = str(fm.get("status", ""))
        if status and status not in VALID_STATUS:
            rep.add("error", "frontmatter", rel, f"invalid status '{status}'")
        if status == "deprecated" and ptype != "source" and not fm.get("superseded_by"):
            rep.add("warning", "deprecated", rel, "deprecated without superseded_by")

        created, updated = parse_date(fm.get("created")), parse_date(fm.get("updated"))
        for k in ("created", "updated"):
            if fm.get(k) and not parse_date(fm.get(k)):
                rep.add("error", "frontmatter", rel, f"{k} is not a YYYY-MM-DD date: {fm.get(k)!r}")
        if created and updated and updated < created:
            rep.add("warning", "dates", rel, "updated is earlier than created")

        srcs = fm.get("sources", [])
        srcs = srcs if isinstance(srcs, list) else [srcs] if srcs else []
        for s in srcs:
            if not re.fullmatch(r"\[\[[^\]]+\]\]", str(s).strip()):
                rep.add("error", "sources", rel, f"sources entry is not a [[wikilink]]: {s!r}")
        if ptype in NEEDS_SOURCES and status in ("growing", "stable") and not srcs:
            rep.add("error", "sources", rel, f"{status} {ptype} page has no sources",
                    "cite source pages or downgrade to seed")

        if rel not in indexed and status != "deprecated":
            rep.add("error", "index", rel, "not listed in index.md", "add a line to index.md")

        if status == "seed" and created and (today - created).days > STALE_SEED_DAYS:
            rep.add("warning", "stale-seed", rel, f"seed for {(today - created).days} days",
                    "grow it, merge it, or deprecate it")
        for m in AS_OF_RE.finditer(p.body):
            d = parse_date(m.group(1))
            if d and (today - d).days > STALE_STATE_DAYS:
                rep.add("warning", "stale-state", rel, f"state fact as of {d} ({(today - d).days} days old)",
                        "re-verify against newer sources")

        if status != "deprecated":
            for name in [fm.get("title", "")] + list(fm.get("aliases") or []):
                key = re.sub(r"[^a-z0-9]+", " ", str(name).lower()).strip()
                if key:
                    titles[key].append(rel)

        # orphans: no inbound link from anything except index/log
        real_in = {s for s in inbound[rel] if s not in ("index.md", "log.md") and not pages[s].is_index_file}
        if not real_in and status != "deprecated":
            rep.add("warning", "orphan", rel, "no inbound links (only index/log)",
                    "link it from related pages")

        # one-way links between wiki pages
        for tgt in sorted(outbound[rel]):
            if tgt in wiki and rel not in outbound[tgt]:
                rep.add("warning", "one-way-link", rel, f"links to [[{Path(tgt).stem}]] but not linked back",
                        f"add a back-reference in {tgt}")

    for key, rels in titles.items():
        uniq = sorted(set(rels))
        if len(uniq) > 1:
            rep.add("warning", "duplicate", ", ".join(uniq), f"same title/alias '{key}'",
                    "merge into one canonical page")

    # --- inbox age
    inbox = ROOT / INBOX
    if inbox.exists():
        for f in sorted(inbox.rglob("*")):
            if f.is_file() and f.name != ".gitkeep" and not f.name.startswith("."):
                age = (today - dt.date.fromtimestamp(f.stat().st_mtime)).days
                if age > STALE_INBOX_DAYS:
                    rep.add("warning", "stale-inbox", f.relative_to(ROOT).as_posix(),
                            f"waiting in inbox for {age} days", "ingest or archive it")

    # --- raw immutability (git)
    changes = git_raw_changes()
    if changes:
        for code, path in changes:
            rep.add("error", "raw-modified", path, f"tracked raw file changed (git status {code})",
                    "restore with git checkout; corrections arrive as new sources")

    # --- notes: most-wanted missing pages
    missing_counts = defaultdict(int)
    for e in rep.items["error"]:
        if e["check"] == "broken-link":
            missing_counts[e["message"].split("]]")[0][2:]] += 1
    for t, n in sorted(missing_counts.items(), key=lambda x: -x[1])[:10]:
        if n >= 2:
            rep.add("note", "wanted-page", "-", f"'{t}' is linked {n} times but has no page")

    inbox_count = len([f for f in inbox.rglob("*") if f.is_file() and f.name != ".gitkeep"]) if inbox.exists() else 0
    stats = {
        "date": today.isoformat(),
        "wiki_pages": len(wiki),
        "sources": sum(1 for r in wiki if r.startswith(f"{WIKI}/sources/")),
        "inbox_items": inbox_count,
        "raw_check": "git" if changes is not None else "skipped (not a git repo)",
    }
    return rep, stats


# --------------------------------------------------------------------------- output

def to_markdown(rep: Report, stats: dict) -> str:
    d = stats["date"]
    out = [
        "---", "type: lint", f"title: Lint {d}", f"created: {d}", "generator: scripts/lint.py", "---", "",
        f"# Lint report: {d}", "",
        f"**Scope:** {stats['wiki_pages']} wiki pages, {stats['sources']} sources, "
        f"{stats['inbox_items']} inbox items · raw check: {stats['raw_check']}", "",
        f"**Summary:** {len(rep.items['error'])} errors · {len(rep.items['warning'])} warnings · "
        f"{len(rep.items['note'])} notes", "",
    ]
    titles = {"error": "Errors (fix first)", "warning": "Warnings", "note": "Notes"}
    for level in ("error", "warning", "note"):
        out.append(f"## {titles[level]}")
        items = rep.items[level]
        if not items:
            out += ["_None._", ""]
            continue
        out += ["| # | Check | Page | Issue | Suggested fix |", "|---|---|---|---|---|"]
        for i, it in enumerate(items, 1):
            msg = it["message"].replace("|", "\\|")
            out.append(f"| {i} | {it['check']} | `{it['page']}` | {msg} | {it['fix']} |")
        out.append("")
    out += ["## Semantic review (agent)",
            "_Mechanical checks above. The agent adds contradictions, uncited claims, and suggested questions here._", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="save report to 50-outputs/lint/")
    ap.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = ap.parse_args(argv)

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    rep, stats = run_checks(today)

    if args.json:
        print(json.dumps({"stats": stats, **rep.items}, indent=2))
    else:
        md = to_markdown(rep, stats)
        print(md)
        if args.write:
            dest = ROOT / "50-outputs" / "lint" / f"{today.isoformat()}-lint.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(md + "\n", encoding="utf-8")
            print(f"\nSaved: {dest.relative_to(ROOT)}", file=sys.stderr)
    return 1 if rep.items["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
