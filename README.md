# humanize-code

[![GitHub stars](https://img.shields.io/github/stars/williamcfrancis/humanize-code?style=flat)](https://github.com/williamcfrancis/humanize-code/stargazers) [![Latest release](https://img.shields.io/github/v/release/williamcfrancis/humanize-code)](https://github.com/williamcfrancis/humanize-code/releases/latest) [![Check package](https://github.com/williamcfrancis/humanize-code/actions/workflows/validate.yml/badge.svg)](https://github.com/williamcfrancis/humanize-code/actions/workflows/validate.yml)

humanize-code makes AI-written code read like a person on your team wrote it, without changing what it does. It is an agent skill for Claude Code, Codex, Cursor, Gemini CLI, and any other agent that reads `SKILL.md`. Its patterns come from AI-code detection research, studies of agent-written pull requests, and the prose patterns in [humanizer](https://github.com/blader/humanizer), which does the same job for writing.

**Before** (written by an AI assistant):

```js
// ==========================================
// Constants
// ==========================================

/** Default currency code used when none is provided */
const DEFAULT_CURRENCY_CODE = 'USD';

/** Fallback text displayed when a price cannot be determined */
const PRICE_UNAVAILABLE_TEXT = 'Price unavailable';

// ==========================================
// Price Formatting
// ==========================================

/**
 * Formats a numeric price into a localized currency string.
 *
 * @param {number} amount - The numeric amount to format.
 * @param {string} [currencyCode='USD'] - The ISO 4217 currency code.
 * @returns {string} The formatted price string.
 */
export function formatPrice(amount, currencyCode = DEFAULT_CURRENCY_CODE) {
  // Validate that the amount is a valid number before formatting
  if (typeof amount !== 'number' || Number.isNaN(amount)) {
    console.warn('⚠️ formatPrice received an invalid amount:', amount);
    return PRICE_UNAVAILABLE_TEXT;
  }

  try {
    // Get the current application locale, falling back to en-US
    const currentLocale = globalThis.__APP_LOCALE__ || 'en-US';

    // Create a new number formatter for the given currency
    const currencyFormatter = new Intl.NumberFormat(currentLocale, {
      style: 'currency',
      currency: currencyCode,
    });

    // Format the amount and return the result
    const formattedPriceString = currencyFormatter.format(amount);
    return formattedPriceString;
  } catch (error) {
    // Handle invalid currency codes gracefully
    console.error('❌ Error formatting price:', error);
    return `${amount.toFixed(2)} ${currencyCode}`;
  }
}
```

**After** (humanize-code with Claude Opus, from the eval suite):

```js
export function formatPrice(amount, currency = 'USD') {
  if (typeof amount !== 'number' || Number.isNaN(amount)) {
    console.warn('formatPrice received an invalid amount:', amount);
    return 'Price unavailable';
  }

  try {
    const locale = globalThis.__APP_LOCALE__ || 'en-US';
    return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(amount);
  } catch (error) {
    // Intl throws a RangeError for an unknown currency code or locale
    console.error('Error formatting price:', error);
    return `${amount.toFixed(2)} ${currency}`;
  }
}
```

The type check stayed, because the API sends one price as the string `"24.50"`. The try/catch stayed, because one product's currency is `"EURO"` and Intl throws on it. The constants were used once, so they moved inline. The one comment left says why the catch is there.

## Results

I compared humanize-code with a plain request ("This project was written by an AI coding assistant and it reads that way. Clean up the code so it looks like an experienced human developer wrote it. Don't change what it does.") using Claude Opus, Sonnet, and Haiku in Claude Code. The project's tests graded each cleanup. Then three Claude judges, playing a code reviewer, an interviewer, and the next maintainer, saw both versions without labels and picked the one that read more like a person wrote it.

| Projects | Skill preferred | Plain request preferred | Tie |
|---|---|---|---|
| The four [eval projects](evals), full of AI tells | 29 | 7 | 0 |
| Two newer projects that Sonnet and Haiku wrote from plain feature requests, with cleaner code | 7 | 10 | 1 |

In the 36 runs of the final version and the plain request, every test, type check, and build still passed, and built output stayed byte-identical. On code full of tells, the skill won with every model. On code that was already fairly clean, the plain request did as well or better: judges rated its cleanups easier to maintain (7.9 against 7.2 out of 10), mostly because it merged duplicated code and dropped JSDoc that the skill kept. The skill made fewer edits there, kept public contracts, and reported bugs instead of fixing them.

The judges are models, each project ran once per model, and I developed the skill against the four eval projects, so the first row is optimistic. That row comes from the last draft before the final rules; the final rules were rerun on those projects for behavior only. The two newer projects shaped the last revision too.

humanize-code edits for the people who review and maintain the code. It is not a way to slip AI output past AI-code detectors or past a project's rules. Before it edits, it reads CONTRIBUTING.md and any AI policy, and it stops if the project does not accept AI-generated code. It never removes AI attribution, such as Co-Authored-By trailers, unless you ask and the project allows it.

## The five strongest tells

These almost never come from a person writing for teammates, so humanize-code acts on a single sighting:

1. **Edit-history comments:** `// Updated to use the new API`, `// Fixed: handle null`
2. **Notes to the prompter:** `// In a real application, you would store this in Redis`
3. **Chat and edit-tool residue:** `// ... existing code ...`, `:contentReference[oaicite:2]`
4. **Emoji in comments and logs:** `console.log('🚀 Server running on port 3000')`
5. **Comments that restate the code**, when most lines have one: `// Initialize the counter`

humanize-code checks for [28 patterns](#the-28-patterns) in all.

## It does not change what the code does

Each of these edits looks like tidying and changes behavior. The eval suite has a test that catches each one:

- `{count > 0 && <Badge />}` rewritten as `{count && <Badge />}` renders a stray `0`.
- Deleting a JSX comment that sits between two lines of text adds a space to the sentence.
- Collapsing `{ active: 'bg-green-100' }` into `` `bg-${color}-100` `` drops the styles, because Tailwind never sees the class name.
- Dropping a `useMemo` that feeds an effect makes the page refetch forever.
- Deleting an "impossible" `instanceof` check leaves an import unused, TypeScript drops it, and the side effect that module ran disappears.
- Replacing a float loop with `sum()` changes the result on Python 3.12 and later.
- Trimming a module docstring changes `--help`, because argparse prints it.

Every pattern says when its fix is safe, or marks itself report only. Before the first edit the agent records a baseline (type check, lint, tests, build, and screenshots when it can run the frontend). It edits in passes from safest to riskiest and checks after each one. It never updates a snapshot to make a test pass. Two scripts help:

- `scan.py` lists likely tells with their pattern numbers.
- `check_cosmetic.py` proves a pass changed only comments and whitespace. It compares Python ASTs, compiles JS, TS and JSX with esbuild (which catches the JSX spacing trap), compares tokens in C-family languages, and fails if a directive comment such as `eslint-disable-next-line` or `# noqa` moved or disappeared.

## Installation

Once installed, the skill answers to `/humanize-code`.

### Claude Code

```text
/plugin marketplace add williamcfrancis/humanize-code
/plugin install humanize-code@humanize-code
```

The plugin answers to `/humanize-code:humanize-code`. To get the short `/humanize-code`, install it with the Skills CLI instead:

```bash
npx skills add williamcfrancis/humanize-code --global --agent claude-code
```

### Codex

```bash
npx skills add williamcfrancis/humanize-code --global --agent codex
```

In Codex, call it as `$humanize-code`.

### Cursor

```bash
npx skills add williamcfrancis/humanize-code --global --agent cursor
```

### Gemini CLI

```bash
gemini extensions install https://github.com/williamcfrancis/humanize-code
```

### Claude.ai and Claude Desktop

Download `humanize-code.zip` from the [latest release](https://github.com/williamcfrancis/humanize-code/releases/latest) and upload it as a skill in Settings.

### Other agents

```bash
npx skills add williamcfrancis/humanize-code --global --agent '*'
```

This installs it for every agent the Skills CLI supports. Leave off `--global` to install it only in the current project. For an agent the Skills CLI does not know, copy the `skills/humanize-code` folder into its skills folder.

## Usage

In a git repository, with no arguments, humanize-code cleans up only the lines your branch changed:

```text
/humanize-code
```

Name files or folders to clean those instead:

```text
/humanize-code src/components src/hooks/useCart.ts
```

Ask for an audit to get a list of findings with pattern numbers and no edits:

```text
/humanize-code audit this branch
```

Paste a snippet to get the rewrite and a short list of what was kept on purpose. Or ask your agent to use humanize-code as a last pass on code it just wrote; in that mode it touches only its own new code.

The scripts also run on their own, with Python 3.9 or later and no dependencies:

```bash
python skills/humanize-code/scripts/scan.py src
python skills/humanize-code/scripts/check_cosmetic.py --base main
```

`scan.py --max 0` exits 1 when it finds anything, so you can run it in CI.

## How it works

A model writes for the widest range of readers and the most cautious reviewer it can imagine, and it sees only part of the repository. So by default it narrates each step, guards against things that cannot happen, builds abstractions for one use, spells out every name and type, leaves traces of the conversation, and writes a fresh helper instead of using the one next door. A person writes for teammates who know the code: they comment the surprising parts, check data where it enters the system, and reuse what exists.

humanize-code reads the human-written code in your repo first and matches its style: its comment density, naming, error handling, and voice. Then it removes the tells strongest first. It does not plant typos or fake TODOs to look human. Those read as staged.

## The 28 patterns

The patterns are grouped and numbered strongest first. Patterns marked *weak alone* count only when other tells are nearby, because a careful developer might write any one of them on purpose. Report-only patterns are found and reported but never edited, because every fix would change behavior.

### A. Leftovers from the chat and the edit

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 1 | **Edit-history comments** | `// Fixed: previously this used float` | Delete it, or state the reason in the present tense |
| 2 | **Notes to the prompter** | `// In a real application, you would use Redis` | Delete it, or state the limitation as a fact |
| 3 | **Chat and edit-tool residue** | `// ... existing code ...`, `oaicite`, a stray code fence | Delete the marker; report missing code |
| 4 | **Emoji in comments and logs** | `logger.info("🧹 Removing stale sessions")` | Remove it everywhere except text users see |

### B. Comments that narrate

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 5 | **Comments that restate the code** | `// Set loading state` above `setLoading(true)` | Delete it |
| 6 | **Docstrings that restate the signature** | `Args: user (User): The user to check.` | Delete it, unless something reads it at runtime |
| 7 | **Deliberation, emphasis, and over-explaining** | `// CRITICAL: Do NOT remove this.` | Give the reason, or report it |
| 8 | **Section banners and labels** (*weak alone*) | `// ===== Helpers =====`, `{/* Header Section */}` | Delete it, except `MARK:` and `#region` |
| 9 | **AI prose in comments and docs** | "serves as the backbone... ensuring a seamless experience" | The fact the code shows |

### C. Defensive by default

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 10 | **try/catch that adds nothing** | `catch (error) { throw error; }` | Remove the try, keep the `await` |
| 11 | **Checks for things that cannot happen** | `if (items === null)` right after `const items = [...]` | Remove it only with proof |
| 12 | **Errors turned into defaults** (*report only*) | `catch { return SAMPLE_PRODUCTS }` | Report which failure is hidden |

### D. Machinery for one use

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 13 | **Abstractions with one implementation** (*weak alone*) | `PriceCalculator` + `PriceCalculatorImpl` + `PriceCalculatorFactory` | One function, when every reference is in the repo |
| 14 | **Helpers and wrappers used once** (*weak alone*) | `_validate_input(x)` that returns `x is not None` | Inline it under the stated conditions |
| 15 | **Dead options, flags, alternatives, and demo code** | `USE_NEW_PARSER = true` beside `parseV1` and `parseV2` | Keep the live path |
| 16 | **Pasted blocks and reimplemented helpers** | Two table builders that differ by one label; a new `formatPrice` beside `formatCents` | One helper, or the existing one if it behaves identically |

### E. Names

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 17 | **Names that spell out the type or say nothing** | `retrievedUserRecordsList`, `data2` | `users`, a domain word |
| 18 | **Iteration leftovers in names** (*weak alone*) | `handleSubmitNew`, `fetchDataV2`, `enhancedParser` | The plain name, when the old one is gone |

### F. Ceremony and uniformity

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 19 | **New code that ignores the file's conventions** | JSDoc on every function in a file that has none | Match the untouched code |
| 20 | **Expression ceremony** (*weak alone*) | `return isValid === true ? true : false` | `return isValid`, when it is a boolean |
| 21 | **Idioms older than the project** | `ioutil.ReadFile` in a Go 1.22 module | `os.ReadFile`, from an allowlist |

### G. Output and debris

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 22 | **Progress chatter and debug output** | `console.log('Fetching users...')` | Delete it, unless something reads it |
| 23 | **Work-report files and throwaway scripts** | `IMPLEMENTATION_SUMMARY.md`, `test_fix.py` | Propose deleting them |
| 24 | **Mock data, placeholders, and leaked agent state** (*report only*) | `api.example.com` on a production path | Report it |

### H. Tests

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 25 | **Tests that cannot fail** (*report only*) | `expect(f(x)).toBe(f(x))`, a special case for a test in production code | Report what is no longer verified |
| 26 | **Test ceremony** (*weak alone*) | `// Arrange`, "should correctly return the value when..." | Drop the scaffold; never touch assertions |

### I. Text around the code

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 27 | **Commit messages and PR descriptions** | `## Summary` with bullets that restate the diff, "✅ All tests pass" | What changed and why, in the repo's style |
| 28 | **Template READMEs and changelogs** (*weak alone*) | `## 🚀 Quick Start`, `- ⚡ **Blazing Fast**` | Plain headings and the project's real commands |

The full rules, with the conditions for each fix and the keep lists, are in [SKILL.md](skills/humanize-code/SKILL.md). Per-language details (JavaScript and TypeScript, React and frontend, Python, Go, Rust, Java and Kotlin, C#, Swift, PHP and Ruby, shell and config files, C and C++) are in [references](skills/humanize-code/references).

## Evals

[`evals/`](evals) holds four small projects written the way coding agents write them, with 32 traps hidden in them, and a runner to prepare, grade, and trap-check a run. Use it to test this skill, another skill, or your own agent setup. See [evals/README.md](evals/README.md).

## Sources

- FMI_SU at SemEval-2026 Task 13, [lightweight detection of LLM-generated code via stylometric signals](https://arxiv.org/html/2605.04157): comment density and verb-led comments.
- [Between Lines of Code](https://arxiv.org/abs/2401.06461) (ICSE 2025): machine code is more regular and more predictable than human code.
- [Whodunit](https://arxiv.org/html/2403.04013v1) (MSR 2024): longer lines and names, more helper functions in GPT-4 code.
- [Human-Written vs. AI-Generated Code](https://arxiv.org/html/2508.21634v1): longer function names and unused arguments in model output.
- Studies of agent pull requests on GitHub: [description length and revisions](https://arxiv.org/html/2509.14745v3) and [message and code consistency](https://arxiv.org/html/2601.04886v2).
- Anthropic's [prompting guidance on over-engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) and the [Claude 3.7 Sonnet system card](https://assets.anthropic.com/m/785e231869ea8b3b/original/claude-3-7-sonnet-system-card.pdf) on special-casing tests.
- [GitClear's 2025 code quality research](https://www.gitclear.com/ai_assistant_code_quality_2025_research) on duplication.
- [humanizer](https://github.com/blader/humanizer) and Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) for the prose patterns.
- Existing cleanup tools whose ideas this builds on, including Cursor's deslop skill, [code-humanizer](https://github.com/LeonardNJU/code-humanizer), and [slop-scan](https://github.com/modem-dev/slop-scan).

## Version history

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT

If humanize-code helps you, a star helps other people find it.
