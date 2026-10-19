# Changelog

## 1.0.0

First release.

- 28 patterns in nine sections, strongest first: leftovers from the chat and the edit, comments that narrate, defensive code, machinery for one use, names, ceremony, output and debris, tests, and the text around code (commits, PRs, READMEs).
- Rule zero: no behavior change, including the rendered UI. Every pattern states when its fix is safe or marks itself report only.
- "Looks cosmetic, isn't" and "Comments that do things" lists in SKILL.md, and per-language reference files with verified hazards and safe modernizations.
- Blind-judged against a plain cleanup request on the eval projects and on two newer projects; see the README for results and their limits.
- `scan.py` lists likely tells. `check_cosmetic.py` proves a pass changed only comments and whitespace (Python AST, esbuild output for JS/TS/JSX, token comparison for C-family languages) and that directive comments stayed in place.
- Eval suite: four fixture projects (vanilla JS and CSS, React and TypeScript, a TypeScript library, a Python CLI) with 32 traps, each caught by the fixture's checks.
- Packages for Claude Code, Codex, Cursor, Gemini CLI, and the Skills CLI.
