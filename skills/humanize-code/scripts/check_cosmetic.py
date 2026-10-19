#!/usr/bin/env python3
"""Check that edits since a git ref changed only comments and whitespace.

    python check_cosmetic.py [--base REF] [paths...]

Run it inside the git repository after a comment-only pass. Each changed file
is compared with its version at REF (default HEAD):

  .py                         AST comparison; docstring edits are reported separately,
                              because some tools read docstrings at runtime
  .js .jsx .mjs .cjs .ts .tsx esbuild output with whitespace minified; this also catches
                              JSX text whose spacing changed (needs esbuild in
                              node_modules/.bin or on PATH, or pass --esbuild)
  .css .scss .less            text with comments removed and whitespace collapsed
  .go .rs .java .kt .cs .c .cc .cpp .h .hpp .swift .scala .dart
                              token comparison with comments removed

In every file, directive comments (eslint-disable, # noqa, //go:build, @ts-expect-error,
'use client', license blocks and so on) must be unchanged, and a next-line directive
must still sit directly above the same line. Exits 1 when anything else changed.
"""

import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

DIRECTIVE = re.compile(
    r"eslint-(disable|enable)|@ts-(ignore|expect-error|nocheck|check)|\bnoqa\b|type:\s*ignore|pyright:|mypy:"
    r"|pylint:\s*(disable|enable)|pragma:\s*no\s*cover|istanbul ignore|c8 ignore|prettier-ignore|fmt:\s*(off|on|skip)"
    r"|isort:\s*skip|\bnolint\b|NOLINT|rubocop:(disable|enable|todo)|shellcheck\s+(disable|source)|stylelint-(disable|enable)"
    r"|swiftlint:(disable|enable)|#pragma\b|ReSharper (disable|restore)|@Suppress|noinspection|@phpstan-ignore|@psalm-suppress"
    r"|phpcs:(ignore|disable|enable)|//\s*ignore(_for_file)?:|checkov:skip|tflint-ignore|hadolint ignore|//go:\w+|//\s*\+build"
    r"|//export \w+|/// <reference|sourceMappingURL|webpack(ChunkName|Ignore|Prefetch|Preload|Mode|Include|Exclude)"
    r"|@vite-ignore|[#@]__PURE__|@jsx(ImportSource|Runtime|Frag)?\b|@flow\b|\+kubebuilder:|@swagger|^\s*--\s*name:"
    r"|translators:|@ngInject|frozen_string_literal|^#!|coding[:=]|#\s*(syntax|escape|check)=|#Requires|@generated"
    r"|@license|@preserve|/\*!|purgecss|rtl:|autoprefixer:|<!--\s*/?ko\b|<!--#|\[if [^\]]*\]|#(end)?region|MARK:"
    r"|['\"]use (client|server|strict)['\"]|falls? ?through",
    re.I,
)
NEXT_LINE = re.compile(r"next-?line|NOLINTNEXTLINE|@ts-(ignore|expect-error)|hadolint ignore|//\s*ignore:|swiftlint:disable:next|shellcheck disable", re.I)

JS = {".js": "jsx", ".jsx": "jsx", ".mjs": "jsx", ".cjs": "jsx", ".ts": "ts", ".mts": "ts", ".cts": "ts", ".tsx": "tsx"}
CSS = {".css", ".scss", ".less"}
C_LIKE = {".go", ".rs", ".java", ".kt", ".kts", ".cs", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".swift", ".scala", ".dart"}


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def old_text(base, path):
    r = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def directive_lines(text):
    lines = [l.strip() for l in text.splitlines()]
    found = Counter(l for l in lines if DIRECTIVE.search(l))
    pairs = Counter()
    for i, line in enumerate(lines):
        if NEXT_LINE.search(line):
            nxt = next((l for l in lines[i + 1:] if l), "")
            pairs[(line, nxt)] += 1
    return found, pairs


def strip_docstrings(tree):
    docs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docs.append(first.value.value)
                node.body = node.body[1:] or [ast.Pass()]
    return docs


def compare_python(before, after):
    try:
        a, b = ast.parse(before), ast.parse(after)
    except SyntaxError as e:
        return "error", f"does not parse: {e}"
    docs_a, docs_b = strip_docstrings(a), strip_docstrings(b)
    if ast.dump(a) != ast.dump(b):
        return "changed", "the AST differs"
    if docs_a != docs_b:
        return "docstrings", "docstrings changed; check that nothing reads them at runtime (argparse, Click, FastAPI, pydantic, doctest)"
    return "same", ""


def find_esbuild(start, override):
    if override:
        return override
    for folder in [start, *start.parents]:
        for name in ("esbuild.cmd", "esbuild.exe", "esbuild"):
            candidate = folder / "node_modules" / ".bin" / name
            if candidate.exists():
                return str(candidate)
    return shutil.which("esbuild")


def esbuild_output(esbuild, loader, text):
    r = subprocess.run([esbuild, f"--loader={loader}", "--minify-whitespace", "--legal-comments=none", "--log-level=error"],
                       input=text, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise ValueError(r.stderr.strip().splitlines()[0] if r.stderr.strip() else "esbuild failed")
    return r.stdout


def first_difference(a, b):
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    return f"before: ...{a[max(0, i - 40):i + 40]!r}\n      after:  ...{b[max(0, i - 40):i + 40]!r}"


REGEX_BEFORE = set("(,=:[!&|?{};+-*%<>~^") | {"return", "typeof", "case", "do", "else", "in", "of", "new",
                                             "delete", "void", "throw", "instanceof", "yield", "await"}


def js_tokens(text):
    """Tokens with comments removed; strings, template literals and regex literals stay whole."""
    tokens, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
        elif ch in "'\"":
            j = i + 1
            while j < n and text[j] != ch and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            tokens.append(text[i:j + 1])
            i = j + 1
        elif ch == "`":
            j, depth = i + 1, 0
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if depth == 0 and text[j] == "`":
                    break
                if text.startswith("${", j):
                    depth, j = depth + 1, j + 2
                    continue
                if depth and text[j] == "}":
                    depth -= 1
                j += 1
            tokens.append(text[i:j + 1])
            i = j + 1
        elif ch == "/" and (not tokens or tokens[-1] in REGEX_BEFORE):
            j, in_class = i + 1, False
            while j < n and text[j] != "\n":
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == "[":
                    in_class = True
                elif text[j] == "]":
                    in_class = False
                elif text[j] == "/" and not in_class:
                    break
                j += 1
            m = re.match(r"[a-z]*", text[j + 1:])
            tokens.append(text[i:j + 1 + m.end()])
            i = j + 1 + m.end()
        else:
            m = re.match(r"[A-Za-z0-9_$]+|\S", text[i:])
            tokens.append(m.group(0))
            i += m.end()
    return tokens


def compare_js(before, after, loader, esbuild):
    if not esbuild:
        if loader in ("jsx", "tsx") and re.search(r"<[A-Za-z>]", before + after) and re.search(r"return\s*\(?\s*<|=>\s*\(?\s*<", before + after):
            return "unchecked", "JSX needs esbuild (npm i -D esbuild, or pass --esbuild)"
        a, b = js_tokens(before), js_tokens(after)
        if a == b:
            return "same", "token check (esbuild not found)"
        k = next((x for x in range(min(len(a), len(b))) if a[x] != b[x]), min(len(a), len(b)))
        if k < min(len(a), len(b)) and len(a[k]) > 40:
            return "changed", "a string or template literal changed\n      " + first_difference(a[k], b[k])
        return "changed", f"tokens differ near {' '.join(a[max(0, k - 5):k + 5])!r} vs {' '.join(b[max(0, k - 5):k + 5])!r}"
    try:
        a, b = esbuild_output(esbuild, loader, before), esbuild_output(esbuild, loader, after)
    except ValueError as e:
        return "error", f"esbuild could not parse it: {e}"
    if a != b:
        return "changed", "compiled output differs\n      " + first_difference(a, b)
    return "same", ""


def normalize_css(text):
    text = re.sub(r"/\*(?!!).*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\s*([{}:;,>~+])\s*", r"\1", text).strip()


STRING_STARTS = re.compile(r'r#*"|R"[^(\s]{0,16}\(|@"|"""|"|\'|`')


def c_like_tokens(text, suffix):
    tokens, i, n = [], 0, len(text)
    code = []
    while i < n:
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if text.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if suffix == ".rs" and text.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            code.append(" ")
            i = j
            continue
        m = STRING_STARTS.match(text, i)
        if m and not (m.group(0) == "'" and suffix == ".rs" and not re.match(r"'(\\.[^']*|[^'\\])'", text[i:i + 12])):
            start = m.group(0)
            if start.startswith("r") and suffix == ".rs":
                end_mark = '"' + "#" * start.count("#")
            elif start.startswith("R\""):
                end_mark = ")" + start[2:-1] + '"'
            elif start == '"""':
                end_mark = '"""'
            elif start == "@\"":
                end_mark = '"'
            elif start == "`" and suffix != ".go":
                code.append(text[i])
                i += 1
                continue
            else:
                end_mark = start
            j = i + len(start)
            while j < n and not text.startswith(end_mark, j):
                if text[j] == "\\" and start not in ("`", "@\"") and not start.startswith(("r", "R")):
                    j += 1
                elif start == "@\"" and text.startswith('""', j):
                    j += 1
                j += 1
            j = min(n, j + len(end_mark))
            tokens.extend(re.findall(r"\w+|\S", "".join(code)))
            code = []
            tokens.append(text[i:j])
            i = j
            continue
        code.append(text[i])
        i += 1
    tokens.extend(re.findall(r"\w+|\S", "".join(code)))
    return tokens


def compare_file(path, before, after, esbuild):
    suffix = path.suffix.lower()
    if suffix == ".py":
        return compare_python(before, after)
    if suffix in JS:
        return compare_js(before, after, JS[suffix], esbuild)
    if suffix in CSS:
        return ("same", "") if normalize_css(before) == normalize_css(after) else ("changed", "CSS differs once comments are removed")
    if suffix in C_LIKE:
        a, b = c_like_tokens(before, suffix), c_like_tokens(after, suffix)
        if a == b:
            return "same", ""
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        return "changed", f"tokens differ near {' '.join(a[max(0, i - 5):i + 5])!r} vs {' '.join(b[max(0, i - 5):i + 5])!r}"
    return "unchecked", f"no checker for {suffix or path.name}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="limit the check to these files or folders")
    parser.add_argument("--base", default="HEAD", help="git ref to compare against (default: HEAD)")
    parser.add_argument("--esbuild", help="path to an esbuild binary")
    args = parser.parse_args()

    root = Path(git("rev-parse", "--show-toplevel").strip())
    os.chdir(root)
    scope = [str(Path(p).resolve().relative_to(root)) for p in args.paths] if args.paths else []
    changed = git("diff", "--name-only", args.base, "--", *scope).split()
    added = git("ls-files", "--others", "--exclude-standard", "--", *scope).split()

    failures = unchecked = docstrings = 0
    for name in sorted(set(changed)):
        path = Path(name)
        before = old_text(args.base, name)
        if before is None:
            print(f"{name}\n      added since {args.base}: not cosmetic")
            failures += 1
            continue
        if not path.exists():
            print(f"{name}\n      deleted: not cosmetic")
            failures += 1
            continue
        after = path.read_text(encoding="utf-8", errors="replace")

        problems = []
        dirs_a, pairs_a = directive_lines(before)
        dirs_b, pairs_b = directive_lines(after)
        for line in (dirs_a - dirs_b):
            problems.append(f"directive removed or reworded: {line[:100]!r}")
        for line in (dirs_b - dirs_a):
            problems.append(f"directive added or reworded: {line[:100]!r}")
        if not problems:
            for directive, target in (pairs_a - pairs_b):
                problems.append(f"next-line directive no longer sits above {target[:60]!r}: {directive[:60]!r}")

        status, detail = compare_file(path, before, after, find_esbuild(path.resolve().parent, args.esbuild))
        label = {"same": "same code", "docstrings": "same code", "unchecked": "NOT CHECKED",
                 "changed": "CODE CHANGED", "error": "ERROR"}[status]
        if problems:
            label = "DIRECTIVE CHANGED" if status in ("same", "docstrings", "unchecked") else label
        print(f"{name}\n      {label}" + (f": {detail}" if detail else ""))
        for p in problems:
            print(f"      {p}")
        failures += status in ("changed", "error") or bool(problems)
        unchecked += status == "unchecked"
        docstrings += status == "docstrings"
    for name in sorted(added):
        print(f"{name}\n      new untracked file: not cosmetic")
        failures += 1

    if not changed and not added:
        print(f"no changes since {args.base}")
    elif failures:
        print(f"\n{failures} file(s) changed more than comments and whitespace")
    else:
        notes = [f"{unchecked} file(s) not checked"] if unchecked else []
        notes += [f"{docstrings} file(s) with docstring changes to review"] if docstrings else []
        print("\nonly comments and whitespace changed" + (f" ({'; '.join(notes)})" if notes else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
