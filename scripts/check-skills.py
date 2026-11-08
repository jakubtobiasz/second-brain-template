#!/usr/bin/env python3
"""Validate agent skills: every .agents/skills/<name>/SKILL.md has frontmatter with a matching
`name` and a `description`, and .claude/skills points at .agents/skills. Exit 1 on problems."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
skills = sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
if not skills:
    errors.append("no skills found in .agents/skills/")
for f in skills:
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{f.relative_to(ROOT)}: missing frontmatter")
        continue
    fm = dict(re.findall(r"^([a-z_-]+):\s*(.*)$", m.group(1), re.M))
    if fm.get("name") != f.parent.name:
        errors.append(f"{f.relative_to(ROOT)}: name '{fm.get('name')}' != folder '{f.parent.name}'")
    if len(fm.get("description", "")) < 40:
        errors.append(f"{f.relative_to(ROOT)}: description missing or too short")
link = ROOT / ".claude" / "skills"
if not link.is_symlink() or link.resolve() != (ROOT / ".agents" / "skills").resolve():
    errors.append(".claude/skills must be a symlink to ../.agents/skills")
for e in errors:
    print(f"error: {e}")
print(f"checked {len(skills)} skills: {'OK' if not errors else f'{len(errors)} error(s)'}")
sys.exit(1 if errors else 0)
