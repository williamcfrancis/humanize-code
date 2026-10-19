# Shell, PowerShell, SQL, and config files: humanize-code reference

Read this with SKILL.md before editing Bash, sh, PowerShell, SQL, YAML, Dockerfile, Terraform, .env, or CI files beyond comments. Tools read most of the text in these files, so when in doubt, report.

## Tells

- **Enterprise template on a tiny script** (§14, §15; weak alone). Color variables, `log_info`/`log_error` and `main() {…}; main "$@"` around three commands. Delete colors and helpers that nothing calls, counting scripts that `source` this one. Unwrap `main` only if nothing sources the script or writes to it while it runs (bash reads a function body whole, but top-level lines as it reaches them), `main "$@"` is its only call, the body has no `local`, `declare`, `typeset`, `return`, `shift` or `$FUNCNAME`, and it goes where the call was, after every function. Keep every line that prints, every `set` and every trap.
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  RED='\033[0;31m'; NC='\033[0m'
  log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
  main() {
      tar -czf "backup-$(date +%F).tgz" ./data
  }
  main "$@"
  ```
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  tar -czf "backup-$(date +%F).tgz" ./data
  ```
- **Exit status hidden by a declaration** (§12; report only). In `local v=$(cmd)`, and the same with `export`, `readonly` or `declare`, `$?` is the declaration's status, which is 0 unless the declaration itself fails. Splitting it changes behavior under `set -e`.
- **Narrated config** (§5; weak alone in Dockerfiles). `# Set the working directory`, a comment per YAML key, `-- Step 1: get active users` over each CTE (CTE-per-step is normal dbt style; the narration is the tell). Delete the narration, never a comment listed below.
- **Banners in .env and YAML** (§8; weak alone). `# ===== Database =====`. Delete only whole lines that start with `#`, and never inside a YAML block scalar (`run: |`) or a quoted multi-line .env value, where the line is text.
- **PowerShell scaffold** (§4, §6, §12; weak alone). Full comment-based help, `[CmdletBinding()] param()`, `Write-Host "✅ Done!"` and a catch that only calls `Write-Error`, on a ten-line script. `Get-Help` prints the help: shrink it only on private helpers and keep its blank lines. Report the catch and keep it: the script runs past the error and `powershell -File` exits 0, where without the catch it stops and exits 1.
- **Defensive SQL** (§11; report only). `DISTINCT` after a join, `COALESCE` on a `NOT NULL` column. Neither is proof of a bug: the join may duplicate rows without a unique key, and a `NOT NULL` column is still NULL on the outer side of a LEFT JOIN and in `MAX` or `SUM` over no rows.
- **Old idioms** (§21). Terraform `"${var.name}"` (medium) and compose `version: '3.8'` (weak alone) have safe fixes below. Report action major bumps such as `actions/checkout@v3`.
- **CI that cannot fail** (§25; report only). `|| true` or `continue-on-error: true` on a test or lint step.
- **Terraform descriptions that restate the name** (§6; report only). terraform-docs and input prompts show them.

## What people write instead

- Bash: commands at top level, a function once something repeats, errors via `echo "…" >&2`, one test style per file.
- PowerShell: Verb-Noun names, full cmdlet names, objects on the output stream, `Write-Verbose` for progress.
- SQL and config: the house keyword case, short aliases, comments only on surprises, quoted versions, exec-form `CMD`.

## Comments that do things

- **Shell:** the shebang; `# shellcheck disable=`, `enable=`, `source=`, `source-path=`, `shell=`; `#` lines inside a heredoc, which are data.
- **PowerShell:** `#Requires` on any line; comment-based help (`.SYNOPSIS`, `.PARAMETER`, `.EXTERNALHELP`, `.FORWARDHELPTARGETNAME`) and its blank lines; a comment directly above a parameter in `param()`, which Get-Help shows as its help when the script or function also has a help block; `<#PSScriptInfo #>`; the `# SIG # Begin signature block`; `#region`.
- **SQL:** sqlc `-- name: GetUser :one`; hints `/*+ … */`; MySQL `/*! … */`; sqlfluff `-- noqa`; dbt `-- depends_on: {{ ref('x') }}`, and any `{{ }}` or `{% %}` inside a `--` comment, which Jinja still runs; PgTyped `/* @name X */`; migration markers (`-- +goose Up`, `-- migrate:up`, `--liquibase formatted sql`, `--changeset`).
- **YAML:** `# yaml-language-server: $schema=`; `# yamllint disable…`; `# renovate:` annotations; the version comment after a SHA pin (`@<sha> # v4.2.2`), which [Renovate reads](https://docs.renovatebot.com/modules/manager/github-actions); `# x-release-please-version`; ansible-lint `# noqa`; every `#` line inside a block scalar (`run: |`), which is script text.
- **Dockerfile:** `# syntax=`, `# escape=`, `# check=`; `# hadolint ignore=` (directly above its instruction), `global ignore=` and `shell=`; `#checkov:skip=`.
- **Terraform:** `#checkov:skip=ID:reason` inside its block; `# tflint-ignore:` (next line); `# tflint-ignore-file:` (top of file only); `#tfsec:ignore:`; `#trivy:ignore:`; `<!-- BEGIN_TF_DOCS -->` in the README.
- **.env:** no directives, but dotenv-safe reads the variable names in `.env.example` and throws when one is unset ([README](https://github.com/rolodato/dotenv-safe)). Do not add or remove variables there.

## Looks cosmetic, isn't

Shell (run with bash 5.3 and dash):
- **Quotes.** With `files="my report.txt"`, `ls $files` gets two arguments and `ls "$files"` one. Unquoted values also glob.
- **`[` to `[[`.** `[ "$x" == a* ]` compares text, after `a*` globs against file names; `[[ $x == a* ]]` matches a pattern. `[ $y = "a b" ]` errors when y has a space or is empty. Where sh is dash, `[[` prints `[[: not found` and the `if` takes the else branch.
- **Splitting `local v=$(cmd)`.** `set -e; f(){ local v=$(false); echo ran; }; f` prints `ran`; split, it exits 1.
- **Inlining a log helper.** `log_error(){ echo "$1" >&2; }` writes to stderr; an inlined `echo` writes to stdout, which callers capture.
- **Adding or removing `set -euo pipefail`.** Under `set -e`, `((i++))` with i at 0 exits. `false | true` returns 0, or 1 with pipefail.
- **Unwrapping `main` in place.** Helpers defined below it do not exist yet. At top level, `local` and `return` fail: the script exits under `set -e` and runs on without it.
- **`cmd; if [ $? -ne 0 ]` to `if ! cmd`.** Under `set -e` the first exits at `cmd`; the second runs the handler.
- **Heredoc indentation.** `<<-END` strips leading tabs; `<<END` keeps them. Turn those tabs into spaces and the spaces stay in the text, and an indented `END` no longer ends the heredoc.
- **Lines added after the shebang.** A `# shellcheck` directive right after the shebang covers the whole file; anywhere else it covers only the next command ([wiki](https://github.com/koalaman/shellcheck/wiki/Directive)). Insert nothing between them.

PowerShell (run with Windows PowerShell 5.1):
- **Dropping the BOM.** Without it, Windows PowerShell 5.1 reads a UTF-8 file in the ANSI code page: on code page 1252, `"café".Length` is 5 and prints `cafÃ©` ([docs](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_character_encoding)). Check that your edit tool keeps it.
- **Write-Host and Write-Output.** A function returns its whole output stream: `function f { Write-Output "Counting..."; 5 }` returns two values, so deleting the chatter changes the result. `$x = f` captures Write-Output, not Write-Host. Removing `| Out-Null` after `$list.Add('x')` on an `ArrayList` adds the index to the result.
- **Blank lines after script help.** Before a function it needs two; with one or none, `Get-Help .\script.ps1` loses the synopsis ([docs](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_comment_based_help)).
- **`#Requires`** applies from any line to the whole script, imports modules, and blocks the run when unmet ([docs](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_requires)).
- **`[CmdletBinding()]`.** Without it and without any `[Parameter()]`, `f extra` runs instead of failing, and common parameters such as `-Verbose` vanish.

SQL (run with SQLite 3.50; PostgreSQL from its docs):
- **NOT IN to NOT EXISTS.** With a NULL in the subquery, `NOT IN` returns no rows.
- **COALESCE around an aggregate.** `SUM` over no rows is NULL; `COALESCE(SUM(x), 0)` is 0.
- **LEFT JOIN filter from ON to WHERE.** Unmatched rows disappear: an inner join.
- **An unread data-modifying CTE.** `WITH d AS (DELETE …)` still runs to completion in PostgreSQL ([docs](https://www.postgresql.org/docs/current/queries-with.html)).
- **Identifier quotes.** PostgreSQL folds unquoted names to lowercase, so `"Users"` and `Users` differ ([docs](https://www.postgresql.org/docs/current/sql-syntax-lexical.html)). In the SQLite library's default build, `SELECT "nosuchcol" FROM users` returns the text, not an error; the CLI turns this off from 3.41 ([docs](https://www.sqlite.org/quirks.html)).

YAML (run with PyYAML 6, a YAML 1.1 loader):
- **Removing quotes.** `3.10` loads as 3.1, `NO`, `yes`, `on` and `off` as booleans, `0755` as 493, `22:22` as 1342. Compose says to quote `HOST:CONTAINER` ports ([docs](https://docs.docker.com/reference/compose-file/services/#ports)). Adding quotes turns numbers into strings.
- **Re-indenting a block scalar.** In `run: |`, indentation beyond the first line's is part of the text, and so is every `#` line.
- **Renaming a GitHub Actions job.** Required checks match by name (the job's `name:`, else its id), so the PR waits for a check that never reports ([docs](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)).
- **Moving `${{ github.event.* }}` from `env:` into `run:`.** Expressions are pasted into the script before the shell runs, so a PR title becomes code ([docs](https://docs.github.com/en/actions/concepts/security/script-injections)). Report the reverse move as a security fix.

Dockerfile ([reference](https://docs.docker.com/reference/dockerfile/)):
- **Anything above a parser directive,** even a blank line: `# syntax=` becomes a plain comment.
- **Exec and shell form.** Shell form runs under `/bin/sh -c`, which does not pass signals, so the app may miss SIGTERM. Exec form does no variable substitution.
- **Merging or splitting RUN** changes layers and caching; `apt-get update` alone in a RUN stays cached ([docs](https://docs.docker.com/build/building/best-practices/)).
- **ENV and ARG.** ENV persists into the container; ARG does not.

Terraform and .env:
- **Renaming a resource label** destroys and recreates the object unless a `moved` block maps it ([docs](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)). Rename locals only.
- **Inline `#` in .env.** `docker run --env-file` keeps it in the value: `PORT=3000 # web` sets `3000 # web` ([docs](https://docs.docker.com/reference/cli/docker/container/run/)). Compose needs a space before it ([docs](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)). Node dotenv 15+ cuts at any `#`, so unquoting `"abc#123"` yields `abc` ([README](https://github.com/motdotla/dotenv)).

## Safe modernizations

- Bash: `$[ x ]` to `$(( x ))`; `function f {` to `f() {` unless an alias named f may exist (files sourced by an interactive shell), since `f() {` expands it; backticks to `$( )` when the command has no backslash or nested backtick and does not start with `(`, because `$((` starts arithmetic.
- PowerShell: `%` to `ForEach-Object` and `?` to `Where-Object`, any version. `ls`, `cat`, `sort` and `rm` to cmdlets only in Windows-only scripts; elsewhere they run native programs ([docs](https://learn.microsoft.com/powershell/scripting/whats-new/unix-support)).
- SQL: `!=` and `<>` in PostgreSQL ([docs](https://www.postgresql.org/docs/current/functions-comparison.html)) and SQLite, with a space after `!=` when `-` or `+` follows, since PostgreSQL reads `!=-` as one operator ([docs](https://www.postgresql.org/docs/current/sql-syntax-lexical.html)); `COUNT(1)` and `COUNT(*)`; keyword case.
- GitHub Actions: `if: ${{ x }}` to `if: x` when the value is that one expression and x starts with a letter or `(`. YAML reads a leading `!` as a tag ([docs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)) and a leading quote, `[` or `{` as YAML syntax.
- Terraform 0.12+, `.tf` files: `"${x}"` to `x`. HCL returns a lone interpolation "without conversion to string" ([spec](https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md)). Not in `.tf.json` or template files, and not as an object key: `{ "${k}" = v }` uses k's value, `{ k = v }` the literal name `k` (write `(k)`).
- Compose: delete top-level `version:` when everything runs Compose v2, which ignores it ([docs](https://docs.docker.com/reference/compose-file/version-and-name/)). Search CI and docs for v1's hyphenated `docker-compose` first.

Not equivalent:
- `#!/bin/bash` to `#!/usr/bin/env bash`: PATH may find another bash.
- `echo -e "$m"` to `printf '%s\n' "$m"`: `\t` stops expanding.
- SQL Server `ISNULL` to `COALESCE`: different type, nullability, and number of evaluations ([docs](https://learn.microsoft.com/sql/t-sql/language-elements/coalesce-transact-sql)).
- `COUNT(col)` to `COUNT(*)`: `COUNT(col)` skips NULLs.
- `MAINTAINER` to `LABEL maintainer=`: one sets the image's Author field, the other a label.

## Verify

- **Shell:** `bash -n new.sh`; `shfmt -mn old.sh > a; shfmt -mn new.sh > b; diff a b` (minify drops comments, so also check the shebang and directives by hand); the same ShellCheck codes as before (`shellcheck -f gcc` line numbers shift when lines go); `git diff --summary` for a lost executable bit. None runs the script, so exit codes and streams go unchecked.
- **PowerShell:** compare code tokens, then diff `Get-Help .\x.ps1 -Full | Out-String` and the first bytes (`EF BB BF`). The parser treats `#Requires` and help as comments, so this function keeps `#Requires` lines and line breaks, and the Get-Help diff covers help:
  ```powershell
  function Code($p) {
    $t = $null; $e = $null
    [void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path $p), [ref]$t, [ref]$e)
    $o = New-Object Collections.Generic.List[string]
    foreach ($k in $t) {
      if ($k.Kind -eq 'Comment' -and $k.Text -notmatch '^#requires') { continue }
      if ($k.Kind -eq 'NewLine') { if ($o.Count -and $o[$o.Count - 1] -ne "`n") { $o.Add("`n") } }
      else { $o.Add($k.Text) }
    }
    ($o -join ' ').Trim()
  }
  (Code old.ps1) -ceq (Code new.ps1)
  ```
- **SQL:** `sqlc diff`; diff `dbt compile` output; PostgreSQL `EXPLAIN (VERBOSE, COSTS OFF)`. For comment passes, compare `sqlparse.format(sql, strip_comments=True)` and grep that hints and `-- name:` lines survive. None shows NULL behavior: run queries on fixtures with NULLs and empty tables.
- **YAML:** diff `python -c "import sys,yaml,json; print(json.dumps(list(yaml.safe_load_all(open(sys.argv[1], encoding='utf-8'))), default=str))" f.yml` (`default=str` handles dates), plus `actionlint`, `docker compose config` or `helm template`. PyYAML is not the real consumer, so never change quoting on its word. Before a job rename, read `gh api repos/OWNER/REPO/branches/BRANCH/protection/required_status_checks` and, for rulesets, `gh api repos/OWNER/REPO/rules/branches/BRANCH`.
- **Dockerfile:** lines before the first instruction byte-identical; unchanged `hadolint` and `docker build --check .`; diff `docker image inspect -f '{{json .Config}}'` of both builds.
- **Terraform:** `terraform validate`, then `terraform plan` matches the baseline plan (no changes when the baseline had none); unchanged `tflint` and `checkov -d .`.
- **.env:** parse with the project's loader before and after, for example `node -e "console.log(require('dotenv').parse(require('fs').readFileSync('.env')))"`.
