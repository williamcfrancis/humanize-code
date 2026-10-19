# Guide for agents

How to change humanize-code without breaking the skill, its package, or its evals.

## What this repo contains

humanize-code is an agent skill written in Markdown, plus two helper scripts and an eval suite. There is no build step.

- `skills/humanize-code/SKILL.md` is the prompt agents read and the source of truth. It explains why AI code looks the way it does, states Rule zero (behavior does not change), and lists numbered patterns grouped in sections, strongest first.
- `skills/humanize-code/references/` holds one file per language family. SKILL.md tells agents to read the matching file before any edit beyond comments.
- `skills/humanize-code/scripts/scan.py` lists likely tells with pattern numbers. `check_cosmetic.py` proves an edit changed only comments and whitespace. Both use only the Python standard library.
- `skills/humanize-code/agents/openai.yaml` holds the display name and default prompt for Codex.
- `evals/` holds four fixture projects with traps, `suite.json` describing their checks and traps, and `run.py` to prepare, grade, and trap-check runs.
- `.claude-plugin/`, `.cursor-plugin/`, `plugin.json` (Agent Plugins 1.0.0), and `gemini-extension.json` are the package manifests.
- `scripts/validate-package.py` checks that all of the above agree.

Keep the skill portable. Do not write instructions that only work in one agent.

## Rules for changes

- **Behavior first.** Every before/after example in SKILL.md and the references must be behavior-identical. If you are not sure, run it. A pattern whose fix can change behavior must say under what conditions it is safe, or be marked report only.
- **Patterns.** Number them from 1 without gaps, grouped by section and strongest first. Fold a new tell into an existing pattern when one already implies it. If you add, remove, or renumber a pattern, update the README tables, the README section title, the `§` references in SKILL.md and the references, and the pattern numbers in `scan.py`.
- **References.** A hazard goes in a reference file only if you ran code that shows it or an official doc states it. Cite the doc.
- **Evals.** A new trap needs a test that fails when the trap is sprung. Run `python evals/run.py check-traps` before you commit; every trap must be caught. Never edit a fixture's snapshots by hand; regenerate them from the untouched fixture code.
- **Version.** Keep one version in SKILL.md `metadata.version`, the first CHANGELOG heading, and every manifest. Do not add a top-level `version` field to SKILL.md.
- **Description.** Every manifest uses the first sentence of the SKILL.md description.
- **Length.** Every word of SKILL.md is read on each use. The validator caps it at 8,000 words; a change that adds words should earn them, and detail that only one language needs belongs in its reference file.
- **History.** Add a CHANGELOG note for any behavior change or non-obvious fix.

## Checks before publishing

```bash
python scripts/validate-package.py
python evals/run.py check-traps
npx skills add . --list
claude plugin validate .
```

## Writing style

Use Plain Language in prompts, docs, comments, and messages: lead with the point, use common words and active voice, keep sentences short, use one term per idea, and use `must` for requirements. Keep exact identifiers, commands, paths, and behavior-bearing examples. Do not use em dashes. This repo is about removing AI tells, so its own text and code should not have them: run the skill on your change before you open a pull request.
