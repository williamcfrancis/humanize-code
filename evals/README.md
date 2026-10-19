# Evals

Four small projects written the way coding agents write them, with traps hidden in them. Each one has tests that pin its output byte for byte. A cleanup passes only when every test still passes and, where there is a build, the build output is identical.

| Fixture | Stack | What the tests pin |
|---|---|---|
| `storefront-js` | Vanilla JS that renders HTML strings, CSS | The rendered page and three cart states, plus the built HTML and CSS |
| `react-dashboard` | React 19, TypeScript, Tailwind classes | Server-rendered HTML, client behavior in jsdom (fetch count, local storage, error state), every class name being spelled out for Tailwind, and the type check |
| `report-lib-ts` | A TypeScript library and CSS, with subtler traps | Every exported function's output, the type check, and the built CSS |
| `python-cli` | Python 3.13 standard library | `--help`, stdout, exit codes, and the CSV and JSON files the CLI writes |

## The traps

Every trap is an edit that looks like tidying and changes behavior. `suite.json` lists all 32 with the reason each one matters. A few examples:

- `{unreadCount > 0 && ...}` rewritten as `{unreadCount && ...}` renders a stray `0`.
- Deleting a JSX comment that sits between two lines of text adds a space to the sentence.
- Collapsing a Tailwind class map into `` `bg-${color}-100` `` drops the styles, because Tailwind never sees the full class names.
- Dropping a `useMemo` that feeds an effect makes the dashboard refetch forever.
- Replacing a float loop with `sum()` changes a total on Python 3.12+ and changes the loyalty points printed.
- Trimming a module docstring changes `--help`, because argparse prints it.
- Removing an "unused" import unregisters the CSV and JSON exporters.
- Rewriting `items += fees` as `items + fees` changes the item count the CLI prints.
- Deleting an "impossible" `instanceof` check leaves an import unused, TypeScript drops it, and a serializer that module registered disappears.
- Shortening `normalizedUserRecords` changes the JSON, because object shorthand made the variable name the output key.

## Running an eval

You need git, Node 20 or newer, and Python 3.13.

```bash
python evals/run.py prepare react-dashboard /tmp/hc-react
```

This copies the fixture, commits a baseline, installs dependencies, and confirms the checks pass. Then run your agent in `/tmp/hc-react` with the skill loaded, for example:

```text
/humanize-code
Clean up this whole repository. Don't touch test/, fixtures/, scripts/, package.json, package-lock.json, or tsconfig.json.
```

Then grade it:

```bash
python evals/run.py grade react-dashboard /tmp/hc-react
```

The grader reports whether protected files are untouched, whether each check passes, whether build output is identical, how the line and comment counts changed, and any comment the agent added about its own cleanup ("// simplified", "// removed redundant check"). It exits non-zero if behavior changed.

## Checking the traps

```bash
python evals/run.py check-traps
```

This applies each trap to a fresh copy of its fixture and confirms the checks fail. If a trap is not caught, the eval cannot detect that mistake, so fix the fixture before trusting a result.

## Adding a fixture

Write the code the way agents write it, add tests that pin every output a user could see, record the snapshots from the untouched code, and add an entry to `suite.json` with its checks, protected paths, and at least five traps. Run `check-traps` before opening a pull request.
