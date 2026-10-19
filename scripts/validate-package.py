#!/usr/bin/env python3
"""Check humanize-code's package files without external dependencies."""

import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "humanize-code"
WORD_CAP = 8000
errors = []


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"Cannot read {path.relative_to(ROOT)}: {e}")


def load_json(path):
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as e:
        sys.exit(f"Fix the JSON in {path.relative_to(ROOT)}: {e}")


skill = read(SKILL_DIR / "SKILL.md")
readme = read(ROOT / "README.md")
changelog = read(ROOT / "CHANGELOG.md")
claude = load_json(ROOT / ".claude-plugin" / "plugin.json")
market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
cursor = load_json(ROOT / ".cursor-plugin" / "plugin.json")
agent_plugin = load_json(ROOT / "plugin.json")
gemini = load_json(ROOT / "gemini-extension.json")

front = re.match(r"\A---\n(.*?)\n---\n", skill, re.S)
if not front:
    sys.exit("SKILL.md must begin with YAML metadata")
meta = front.group(1)
for key in ("version:", "compatibility:", "allowed-tools:"):
    if re.search(rf"(?m)^{re.escape(key)}", meta):
        errors.append(f"Remove the unportable top-level YAML field {key[:-1]}")
name = re.search(r"(?m)^name:\s*(\S+)\s*$", meta)
if not name or name.group(1) != SKILL_DIR.name:
    errors.append("The SKILL.md name must match its folder, humanize-code")

desc_block = re.search(r"(?m)^description: \|\n((?:  .*\n)+)", meta + "\n")
if not desc_block:
    sys.exit("Write the SKILL.md description as an indented block")
description = " ".join(desc_block.group(1).split())
first_sentence = description.split(". ")[0].rstrip(".") + "."
if len(description) > 1024:
    errors.append(f"Keep the SKILL.md description under 1,024 characters (it has {len(description)})")
if len(first_sentence) > 200:
    errors.append("Keep the first sentence of the description under 200 characters for claude.ai")

version = re.search(r'(?m)^\s+version:\s*["\']?(\d+\.\d+\.\d+)["\']?\s*$', meta)
if not version:
    sys.exit("Add metadata.version to SKILL.md as a three-part version")
changelog_version = re.search(r"(?m)^## (\d+\.\d+\.\d+)$", changelog)
versions = {
    "SKILL.md": version.group(1),
    "CHANGELOG.md": changelog_version.group(1) if changelog_version else "",
    ".claude-plugin/plugin.json": str(claude.get("version", "")),
    ".cursor-plugin/plugin.json": str(cursor.get("version", "")),
    "plugin.json": str(agent_plugin.get("version", "")),
    "gemini-extension.json": str(gemini.get("version", "")),
}
if len(set(versions.values())) != 1:
    errors.append(f"Use one version everywhere: {versions}")

descriptions = {
    ".claude-plugin/plugin.json": claude.get("description"),
    ".cursor-plugin/plugin.json": cursor.get("description"),
    "plugin.json": agent_plugin.get("description"),
    "gemini-extension.json": gemini.get("description"),
    **{f"marketplace.json:{p.get('name')}": p.get("description") for p in market.get("plugins", [])},
}
for where, text in descriptions.items():
    if text != first_sentence:
        errors.append(f"{where} description must be the first sentence of the SKILL.md description")

names = {claude.get("name"), cursor.get("name"), agent_plugin.get("name"), gemini.get("name"), market.get("name"),
         *(p.get("name") for p in market.get("plugins", []))}
if names != {"humanize-code"}:
    errors.append(f"Use the name humanize-code in every manifest: {sorted(map(str, names))}")
if "skills" in claude or "skills" in cursor:
    errors.append("Omit the skills key so Claude Code and Cursor scan skills/ by default")
if set(agent_plugin) - {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}:
    errors.append("plugin.json allows only the Agent Plugins 1.0.0 fields")

skill_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("SKILL.md") if "node_modules" not in p.parts)
if skill_files != ["skills/humanize-code/SKILL.md"]:
    errors.append(f"Keep exactly one SKILL.md, in skills/humanize-code: {skill_files}")

patterns = {int(n): t for n, t in re.findall(r"(?m)^### (\d+)\. (.+)$", skill)}
numbers = list(patterns)
if numbers != list(range(1, len(numbers) + 1)):
    errors.append(f"Number the SKILL.md patterns from 1 without gaps: {numbers}")
readme_patterns = {int(n): t for n, t in re.findall(r"(?m)^\| (\d+) \| \*\*(.+?)\*\*", readme)}
if sorted(readme_patterns) != numbers:
    errors.append(f"List patterns 1 to {len(numbers)} once each in the README tables: {sorted(readme_patterns)}")
for n, title in patterns.items():
    if n in readme_patterns and readme_patterns[n] != title:
        errors.append(f"README pattern {n} is {readme_patterns[n]!r}; SKILL.md calls it {title!r}")
if f"## The {len(numbers)} patterns" not in readme:
    errors.append(f"Title the README pattern section 'The {len(numbers)} patterns'")

for path in [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").glob("*.md"))]:
    bad = sorted({int(n) for n in re.findall(r"§(\d+)", read(path)) if not 1 <= int(n) <= len(numbers)})
    if bad:
        errors.append(f"{path.relative_to(ROOT)} points at patterns that do not exist: {bad}")

words = len(skill.split())
if words > WORD_CAP:
    errors.append(f"Keep SKILL.md at {WORD_CAP:,} words or fewer; it has {words:,}")
if not list((SKILL_DIR / "references").glob("*.md")):
    errors.append("skills/humanize-code/references/ has no language files")
for script in sorted((SKILL_DIR / "scripts").glob("*.py")) + [ROOT / "evals" / "run.py"]:
    try:
        py_compile.compile(str(script), doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(f"{script.relative_to(ROOT)} does not compile: {e.msg}")
    rel = script.relative_to(SKILL_DIR).as_posix() if SKILL_DIR in script.parents else None
    if rel and rel not in skill:
        errors.append(f"SKILL.md never mentions {rel}")

suite = load_json(ROOT / "evals" / "suite.json")["fixtures"]
traps = 0
for fixture, spec in suite.items():
    folder = ROOT / "evals" / "fixtures" / fixture
    if not folder.is_dir():
        errors.append(f"evals/suite.json names a missing fixture: {fixture}")
        continue
    for mutation in spec["mutations"]:
        traps += 1
        for edit in mutation["edits"]:
            target = folder / edit["file"]
            if not target.exists() or edit["find"] not in read(target):
                errors.append(f"trap {fixture}/{mutation['id']} no longer matches {edit['file']}")
match = re.search(r"lists all (\d+)", read(ROOT / "evals" / "README.md"))
if match and int(match.group(1)) != traps:
    errors.append(f"evals/README.md says {match.group(1)} traps; suite.json has {traps}")

if errors:
    print("\n".join(f"- {e}" for e in errors))
    sys.exit(1)
print(f"humanize-code v{versions['SKILL.md']} is valid: {len(numbers)} patterns, {words:,} words, {traps} traps")
