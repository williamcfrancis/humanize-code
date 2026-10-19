#!/usr/bin/env python3
"""List likely signs of AI-written code, tagged with humanize-code pattern numbers.

    python scan.py [paths...] [--json] [--max N]

The output is a list of hints for a person or an agent to review. A line can be
flagged and still be fine; read SKILL.md before changing anything. Standard
library only.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "out", ".next", ".nuxt", "coverage",
    "__pycache__", ".venv", "venv", "env", "target", ".cache", "bin", "obj", ".turbo", ".idea",
}
SKIP_FILES = re.compile(r"(\.min\.(js|css)$|(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Cargo\.lock|go\.sum)$)")

SLASH = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".kt", ".kts", ".go", ".rs", ".c", ".h",
         ".cc", ".cpp", ".hpp", ".cs", ".swift", ".scala", ".dart", ".php", ".scss", ".less", ".vue", ".svelte"}
HASH = {".py", ".rb", ".sh", ".bash", ".zsh", ".ps1", ".yml", ".yaml", ".toml", ".r", ".pl", ".tf", ".env"}
BLOCK_ONLY = {".css"}
HTML = {".html", ".htm", ".vue", ".svelte"}
SQL = {".sql"}
DOCS = {".md", ".mdx", ".rst"}
JS_LIKE = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆↔-↪⃣️]")

PATTERNS = [
    (1, "edit-history comment", re.compile(
        r"^(updated|fixed|changed|modified|refactored|replaced|removed|added|new|now)\b\s*[:(-]"
        r"|\b(previously|used to|no longer needed|per (the )?review|as per review|was changed|changed from|instead of the old)\b"
        r"|\((was|previously|old|updated|new)\b", re.I)),
    (2, "note to the prompter", re.compile(
        r"\bin a real[- ](app|application|world|project|implementation|scenario|system)\b|\bin production,? you\b"
        r"|\breplace (this |these |it )?with (your|the actual|real|actual)\b|\byour[-_ ]?(api[-_ ]?key|token|secret|domain)\b"
        r"|\byou (can|may|might|could|should|will) (want to )?(extend|customi[sz]e|modify|adjust|change|add|replace|tweak)\b"
        r"|\badd more .{0,30}(if|as) needed\b|\bfor (simplicity|demonstration|demo purposes|illustration)\b"
        r"|\bas requested\b|\bper (the|your) (requirements?|spec|instructions)\b|\b(step|phase) \d+ of (the|this) plan\b", re.I)),
    (3, "chat or edit-tool residue", re.compile(
        r"contentReference|oaicite|turn\d+(search|news|view)\d+|【\d+†|\[cite: ?\d+\]|utm_source=(chatgpt|openai|copilot)"
        r"|\.\.\.\s*(existing|rest of|remaining|other|previous) (code|implementation|the (code|function|file))"
        r"|\b(rest of|remaining) (the )?(code|function|file) (remains|stays|is) (the same|unchanged)\b|TODO\(human\)"
        r"|^here'?s (the|an?) (updated|complete|full|revised|corrected|fixed)\b", re.I)),
    (7, "emphasis or deliberation", re.compile(
        r"^(critical|important|note|warning)\b.{0,10}(do not|don't|never|must)\b(?!.*\bbecause\b)"
        r"|\bwe (considered|evaluated|decided|chose)\b|\bafter (careful(ly)? )?evaluating\b|\btrade-?offs? between\b"
        r"|\*\*[^*]+\*\*|^#{2,}\s", re.I)),
    (9, "AI prose", re.compile(
        r"\b(robust(ly|ness)?|comprehensive(ly)?|seamless(ly)?|leverag(e|es|ed|ing)|utili[sz](e|es|ed|ing)|facilitat\w*"
        r"|ensur(e|es|ing) that|gracefully|elegant(ly)?|enhanced?|streamlin\w*|production-ready|blazing(ly)?[- ]fast"
        r"|cutting-edge|state-of-the-art|load-bearing|genuinely|serves as (the|a|an)|plays a (crucial|key|vital|pivotal) role"
        r"|not (just|only|merely) .{1,60},? but)\b", re.I)),
]

RESTATE_VERBS = (
    "initiali[sz]e|create|define|declare|set|get|loop|iterate|return|check|call|import|increment|decrement|add|update"
    "|calculate|compute|handle|store|fetch|render|validate|convert|build|append|log|print|parse|read|write|open|close"
    "|assign|instantiate|load|save|send|filter|map|sort|extract|format|generate|process|apply|make|find|remove|delete"
    "|clear|reset|wait|start|stop|run|execute|show|display|hide|toggle|register|export|mark|trim|split|join|merge"
)
RESTATING = re.compile(rf"^(({RESTATE_VERBS})(s|es|ing)?\b|step \d+\b|(first|next|then|finally),)", re.I)
BANNER = re.compile(r"^[\s=\-*#~_/+]*([=\-*#~_+]{4,})|^\s*[=\-*#~]{2,}.{0,40}[=\-*#~]{2,}\s*$|\bsection\s*$", re.I)
TEMPLATE_ERRORS = re.compile(r"HTTP error! ?status|An unknown error occurred|An error occurred while|An unexpected error occurred|error instanceof Error \? error\.message")
LOG_CALL = re.compile(r"\b(console\.(log|info|debug|warn|error)|print|logger\.\w+|logging\.\w+|log\.\w+|Write-Host|echo)\s*\(?\s*f?[\"'`]")
CHATTER = re.compile(r"[\"'`]\s*\W{0,4}\s*(starting|fetching|loading|processing|initiali[sz]ing|done|completed|finished|all done|success(fully)?)\b|successfully\b|\bmounted\b|[\"'`]=+[\"'`]\s*\*", re.I)
DEF_NAME = re.compile(r"\b(?:function|def|class|const|let|var|fn|func|interface|type)\s+([A-Za-z_][A-Za-z0-9_]*)")
ITERATION_NAME = re.compile(r"(?:New|V\d+|_v\d+|Fixed|_fixed|Final|_final|Enhanced|Improved|Updated|Refactored|Optimized|_new|_old|Old|Backup|_backup|Copy|_copy)$|^(enhanced|improved|updated)[A-Z_]")
# versions that belong to a spec, not to an earlier draft: UUID_V4, isIPv6, OAUTH_V2
SPEC_VERSION = re.compile(r"(?:(?:^|_)(?i:uuid|ip|oauth|tls|ssl|api)|(?<=[a-z0-9])(?:Uuid|UUID|Ip|IP|OAuth|OAUTH|Tls|TLS|Ssl|SSL|Api|API))_?[Vv]\d+$")
PLACEHOLDER = re.compile(r"your[-_]?api[-_]?key|YOUR_[A-Z_]*KEY|sk-x{4,}|api\.example\.com|/path/to/your|/mnt/data/|\bchangeme\b", re.I)
TEST_CEREMONY = re.compile(r"^(arrange|act|assert)\b\s*$|\bshould (correctly|properly|successfully)\b", re.I)
DEBRIS_FILE = re.compile(
    r"(^|/)([A-Z_]*(SUMMARY|IMPLEMENTATION|_REPORT|FINAL_STATUS|READY_FOR_[A-Z]+|SESSION_[A-Z0-9_\-]*)[A-Z0-9_\-]*\.md"
    r"|test_fix\w*\.py|verify_\w+\.(py|js|ts)|debug_\w+\.(py|js|ts|mjs)|tmpclaude-[\w-]*|[\w-]+\.bak|[\w-]+_(old|backup|v\d+|new|fixed)\.\w+)$")
JSDOC_TYPES = re.compile(r"@(param|returns?)\s*\{")
MD_TELLS = re.compile(r"^#{1,6} .*[\U0001F300-\U0001FAFF☀-➿]|blazing(ly)?[- ]fast|contributions are welcome|yourusername|\b\d{4}-XX-XX\b", re.I)


def iter_files(paths):
    for root in paths:
        root = Path(root)
        if root.is_file():
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                yield Path(dirpath) / name


def comment_markers(path):
    suffix = path.suffix.lower()
    if path.name == "Dockerfile" or path.name.startswith(".env"):
        return ("#",), ()
    line = ("//",) if suffix in SLASH else ("#",) if suffix in HASH else ("--",) if suffix in SQL else ()
    if suffix == ".php":
        line = ("//", "#")
    block = [("/*", "*/")] if suffix in SLASH | BLOCK_ONLY | SQL else []
    if suffix in HTML:
        block.append(("<!--", "-->"))
    return line, tuple(block)


def comments(text, path):
    """Yield (line_number, comment_text, is_doc) for each comment, skipping string contents."""
    line_marks, blocks = comment_markers(path)
    python = path.suffix.lower() == ".py"
    quotes = ("'", '"', "`") if path.suffix.lower() in JS_LIKE else ("'", '"')
    i, n, line = 0, len(text), 1
    at_statement_start = True
    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            at_statement_start = True
            i += 1
            continue
        if python and text.startswith(('"""', "'''"), i):
            delim = text[i:i + 3]
            end = text.find(delim, i + 3)
            end = n if end == -1 else end
            body = text[i + 3:end]
            if at_statement_start:
                for k, part in enumerate(body.splitlines()):
                    if part.strip():
                        yield line + k, part.strip(), True
            line += body.count("\n")
            i = end + 3
            at_statement_start = False
            continue
        if ch in quotes:
            j = i + 1
            while j < n and text[j] != ch:
                if text[j] == "\\":
                    j += 1
                elif text[j] == "\n":
                    if ch != "`":
                        break
                    line += 1
                j += 1
            i = j + 1
            at_statement_start = False
            continue
        matched = False
        for start, end_mark in blocks:
            if text.startswith(start, i):
                end = text.find(end_mark, i + len(start))
                end = n if end == -1 else end
                body = text[i + len(start):end]
                for k, part in enumerate(body.splitlines()):
                    part = part.strip().lstrip("*").strip()
                    if part:
                        yield line + k, part, start == "/*" and body.startswith("*")
                line += body.count("\n")
                i = end + len(end_mark)
                matched = True
                break
        if matched:
            continue
        for mark in line_marks:
            if text.startswith(mark, i) and not (mark == "//" and i > 0 and text[i - 1] == ":"):
                end = text.find("\n", i)
                end = n if end == -1 else end
                yield line, text[i + len(mark):end].strip().lstrip("/!").strip(), False
                i = end
                matched = True
                break
        if matched:
            continue
        if not ch.isspace():
            at_statement_start = False
        i += 1


def scan_file(path, rel):
    findings = []
    add = lambda line, pattern, kind, snippet: findings.append(
        {"file": rel, "line": line, "pattern": pattern, "kind": kind, "text": snippet.strip()[:120]})

    if DEBRIS_FILE.search(rel.replace("\\", "/")):
        add(0, 23, "work-report or throwaway file", rel)
    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return findings, None
    head = text[:600]
    if "@generated" in head or ("Code generated" in head and "DO NOT EDIT" in head):
        return findings, None

    if suffix in DOCS:
        for n, line in enumerate(text.splitlines(), 1):
            if MD_TELLS.search(line):
                add(n, 28, "template README or changelog", line)
            if PATTERNS[4][2].search(line) and not line.lstrip().startswith(("|", "```")):
                add(n, 9, "AI prose", line)
        return findings, None

    if not comment_markers(path)[0] and not comment_markers(path)[1]:
        return findings, None

    lines = text.splitlines()
    code_lines = sum(1 for l in lines if l.strip())
    comment_rows = set()
    restating = []
    in_test = bool(re.search(r"(^|/)(tests?|__tests__|spec)(/|$)|[._-](test|spec)\.\w+$|^test_", rel.replace("\\", "/")))

    for n, body, is_doc in comments(text, path):
        comment_rows.add(n)
        if EMOJI.search(body):
            add(n, 4, "emoji in comment", body)
        for number, kind, rx in PATTERNS:
            if rx.search(body):
                add(n, number, kind, body)
        if BANNER.search(body):
            add(n, 8, "section banner", body)
        if not is_doc and RESTATING.search(body) and len(body.split()) <= 10:
            restating.append((n, body))
        if suffix in {".ts", ".tsx"} and JSDOC_TYPES.search(body):
            add(n, 6, "JSDoc type that repeats the TypeScript signature", body)
        if is_doc and re.search(r"time complexity|space complexity", body, re.I):
            add(n, 6, "complexity note in a docstring", body)
        if in_test and TEST_CEREMONY.search(body):
            add(n, 26, "test ceremony", body)

    if len(restating) >= 3:
        for n, body in restating:
            add(n, 5, "comment that restates the code", body)

    for n, line in enumerate(lines, 1):
        if n in comment_rows:
            continue
        if LOG_CALL.search(line):
            if EMOJI.search(line):
                add(n, 4, "emoji in a log or print string", line)
            if CHATTER.search(line):
                add(n, 22, "progress chatter", line)
        if TEMPLATE_ERRORS.search(line):
            add(n, 12, "template error handling", line)
        if PLACEHOLDER.search(line) and not in_test:
            add(n, 24, "placeholder or sandbox value", line)
        if line.strip().startswith("```"):
            add(n, 3, "Markdown fence in a source file", line)
        for name in DEF_NAME.findall(line):
            if ITERATION_NAME.search(name) and not SPEC_VERSION.search(name):
                add(n, 18, "iteration-leftover name", name)
        if in_test and TEST_CEREMONY.search(line) and re.search(r"\b(it|test|def test)\b", line):
            add(n, 26, "test name ceremony", line)

    density = len(comment_rows) / code_lines if code_lines else 0
    if code_lines >= 20 and density >= 0.3:
        add(0, 5, "comment density", f"{len(comment_rows)} of {code_lines} non-blank lines are comments ({density:.0%})")
    return findings, {"lines": code_lines, "comment_lines": len(comment_rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--max", type=int, help="exit 1 when there are more findings than this")
    args = parser.parse_args()

    findings, stats = [], {}
    base = Path.cwd()
    for path in iter_files(args.paths):
        try:
            rel = str(path.resolve().relative_to(base))
        except ValueError:
            rel = str(path)
        if SKIP_FILES.search(rel.replace("\\", "/")):
            continue
        found, info = scan_file(path, rel)
        findings.extend(found)
        if info:
            stats[rel] = info

    findings.sort(key=lambda f: (f["file"], f["line"], f["pattern"]))
    if args.json:
        print(json.dumps({"findings": findings, "files": stats}, indent=2, ensure_ascii=False))
    else:
        current = None
        for f in findings:
            if f["file"] != current:
                current = f["file"]
                print(current)
            where = f"{f['line']:>5}" if f["line"] else "     "
            print(f"{where}  §{f['pattern']:<3} {f['kind']}: {f['text']}")
        by_pattern = {}
        for f in findings:
            by_pattern[f["pattern"]] = by_pattern.get(f["pattern"], 0) + 1
        summary = ", ".join(f"§{p} x{c}" for p, c in sorted(by_pattern.items()))
        print(f"\n{len(findings)} findings in {len({f['file'] for f in findings})} files" + (f" ({summary})" if summary else ""))
    if args.max is not None and len(findings) > args.max:
        sys.exit(1)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
