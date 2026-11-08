#!/usr/bin/env python3
"""PreToolUse hook: protect 10-raw/ (immutable sources) and 40-journal/ (owner's writing).

Rules (AGENTS.md section 6):
  10-raw/      may only GROW: moving or copying a new file in is allowed.
               Editing, overwriting, deleting, or moving files out is blocked.
  40-journal/  is read-only for the agent: any write, move, or delete is blocked.

Exit code 2 blocks the tool call, and stderr is shown to the agent.
This is a guardrail against mistakes, not a sandbox: the Bash check is heuristic.
The owner can always edit these folders directly (Obsidian, editor).
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()
RAW = (ROOT / "10-raw").resolve()
JOURNAL = (ROOT / "40-journal").resolve()

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
DESTRUCTIVE = {"rm", "rmdir", "unlink", "truncate", "shred", "chmod", "chown", "touch", "ln", "dd", "tee"}
IN_PLACE = {"sed", "perl", "gsed"}  # blocked only with -i
SEPARATORS = {";", "&&", "||", "|", "&"}


def block(msg: str):
    print(f"Blocked by .claude/hooks/protect_paths.py: {msg}\n"
          "See AGENTS.md section 6 (hard rules). Ask the owner if this is really needed; "
          "they can make the change directly.", file=sys.stderr)
    sys.exit(2)


def resolve(p: str, cwd: Path) -> Path:
    path = Path(os.path.expanduser(p))
    if not path.is_absolute():
        path = cwd / path
    # resolve without requiring existence
    return Path(os.path.normpath(str(path)))


def area(p: Path):
    for name, base in (("10-raw", RAW), ("40-journal", JOURNAL)):
        try:
            p.relative_to(base)
            return name
        except ValueError:
            pass
    return None


def check_write_tool(name: str, tool_input: dict, cwd: Path):
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return
    p = resolve(target, cwd)
    a = area(p)
    if a == "40-journal":
        block(f"{name} on {p.relative_to(ROOT)}: 40-journal/ is the owner's writing (read-only for the agent).")
    if a == "10-raw":
        if name == "Write" and not p.exists():
            return  # adding a brand-new source file is allowed
        block(f"{name} on {p.relative_to(ROOT)}: 10-raw/ is immutable. Corrections arrive as new sources.")


def split_segments(command: str):
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        tokens = command.split()
    seg = []
    for t in tokens:
        if t in SEPARATORS:
            if seg:
                yield seg
            seg = []
        else:
            seg.append(t)
    if seg:
        yield seg


def check_bash(command: str, cwd: Path):
    if "10-raw" not in command and "40-journal" not in command and not area(cwd.resolve()):
        return  # fast path: no protected path mentioned and not running inside one

    # Output redirection into a protected area: > or >>
    for m in re.finditer(r"(?<![0-9&<])>{1,2}\s*([^\s;&|]+)", command):
        a = area(resolve(m.group(1).strip("'\""), cwd))
        if a:
            block(f"shell redirection into {a}/ ('{m.group(0).strip()}').")

    for seg in split_segments(command):
        # drop env assignments and sudo/command prefixes
        while seg and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[0]) or seg[0] in ("sudo", "command", "nohup")):
            seg = seg[1:]
        if not seg:
            continue
        verb = Path(seg[0]).name
        args = seg[1:]
        if verb == "git" and args:
            verb, args = "git " + args[0], args[1:]
        paths = [a for a in args if not a.startswith("-")]
        flags = [a for a in args if a.startswith("-")]
        areas = [(p, area(resolve(p, cwd))) for p in paths]
        hit = [(p, a) for p, a in areas if a]
        if not hit:
            continue

        if verb in DESTRUCTIVE or verb in ("git rm", "git clean", "git checkout", "git restore"):
            if verb == "git checkout" or verb == "git restore":
                continue  # restoring a raw file to its committed state is fine
            block(f"'{verb}' on {hit[0][0]} ({hit[0][1]}/ is protected).")

        if verb in IN_PLACE and any(f.startswith("-i") or f == "--in-place" for f in flags):
            block(f"in-place edit with '{verb}' on {hit[0][0]}.")

        if verb in ("mv", "git mv", "cp", "rsync", "install"):
            if len(paths) < 2:
                continue
            *srcs, dest = paths
            dest_p = resolve(dest, cwd)
            dest_a = area(dest_p)
            for s in srcs:
                s_a = area(resolve(s, cwd))
                if verb in ("mv", "git mv") and s_a:
                    block(f"moving {s} out of / within {s_a}/ (files there must stay put).")
            if dest_a == "40-journal":
                block(f"'{verb}' into 40-journal/ (owner's writing).")
            if dest_a == "10-raw":
                # no overwriting existing raw files
                for s in srcs:
                    final = dest_p / Path(s).name if dest_p.is_dir() else dest_p
                    if final.exists():
                        block(f"'{verb}' would overwrite existing raw file {final.relative_to(ROOT)}. "
                              "Use a new dated file name.")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    cwd = Path(data.get("cwd") or os.getcwd())
    if name in WRITE_TOOLS:
        check_write_tool(name, tool_input, cwd)
    elif name == "Bash":
        check_bash(tool_input.get("command", ""), cwd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
