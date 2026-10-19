# JavaScript and TypeScript: humanize-code reference

Read this with SKILL.md before you edit JavaScript, TypeScript or Node.js code beyond comments. Framework UI code has its own file.

## Tells

- **Restating JSDoc in .ts files** (§6, medium): `@param {string} email - The email` above `email: string`. tsc ignores JSDoc types in .ts files, so delete the braces and lines that repeat the name. In .js files the JSDoc is the type under `checkJs` or `// @ts-check`, and also when `allowJs` and `declaration` build `.d.ts` files from it, even without `checkJs`: keep it. A `.ts` file that imports a .js module under `allowJs` also reads its JSDoc, including the types internal functions pass into exported ones. Where nothing reads it, editors still show JSDoc types on hover: keep them on a library's exports, on exported functions that take or return a union, object shape, or callback, and on any `@typedef` another file names (`import('./types.js').User`), and delete the rest, such as the same `@type` above every handler and `@param {string} id` on one-liners. Keep `@deprecated`, `@throws`, `@example`, `@internal` under `stripInternal`, and docs TypeDoc publishes.
- **Pasted blocks** (§16, medium): `sendJson` and `sendEmpty` that repeat the same default headers and the same `res.writableEnded` guard. Merge the shared part under §16's conditions: keep the guard ahead of any work it skipped (`JSON.stringify(data)` passed as an argument runs before the helper's guard and can throw where the old code returned), keep each caller's own `return`, and give each response a fresh headers object (`{ ...BASE_HEADERS, ...headers }`) if anything adds to it later.
- **Mapping ladders** (§20, weak alone): `if (err.code === 'HPE_HEADER_OVERFLOW') status = 431; else if (…) status = 408; else if (…)` becomes a `Map` or an `Object.hasOwn`-guarded object keyed by the code (see Lookup tables below).
- **Exports nothing imports** (§15, medium, applications only): `export const MAX_TAGS = 20` read only inside its own module. Drop `export` after the search §15 describes. If the module never reads the name itself, dropping `export` leaves an unused local (`noUnusedLocals`, `no-unused-vars`): report it instead.
- **Rethrow-only catch** (§10, medium): `catch (err) { throw err; }`. Remove the try only when the catch does nothing else. Keep `finally`, and keep `return await` inside any remaining try.
- **Null-check ladders** (§11, medium): `x !== null && x !== undefined` becomes `x != null`. `users && users.length > 0` becomes `users?.length` only as a condition and only when `users` is an array or nullish; as values they differ. Remove `?.` only after a `const` set from a literal or `new` in the same function.
- **Spread fallbacks** (§11, weak alone): `{ ...(opts || {}) }` becomes `{ ...opts }` in an object literal. Never in array or call spreads: `[...undefined]` throws.
- **Double casts and bare suppressions** (§20, weak alone): `const user = (await res.json()) as unknown as User` needs one cast at most: `const user: User = await res.json()` where `json()` returns `any` (DOM lib), `(await res.json()) as User` where it returns `unknown` (@types/node alone). Casts and annotations erase, so the output is the same. Delete a `@ts-ignore` only if `tsc --noEmit` passes without it for every tsconfig that includes the file. Never swap a cast for a runtime check or `?.`. Report `// @ts-nocheck`.
- **Inferred annotations** (§20, weak alone): `let count: number = 0`. Remove only when the inferred type is identical: `let count = 0` infers `number`, but `const count = 0` infers the literal type `0`. Keep `string[] = []`, literal and union types (`let mode: Mode = 'a'` widens to `string` without one), export return types that `isolatedDeclarations` or lint requires, and annotations on decorated classes under `emitDecoratorMetadata`.
- **Async noise** (§20, weak alone): `const [user] = await Promise.all([getUser(id)])` becomes `const user = await getUser(id)` only when nothing else reads the array and no code depends on microtask order, because the unwrapped form settles one microtask sooner. `return await` is not a tell: removing it changes timing and async stack traces, and inside try/catch it is what lets the catch see a rejection.
- **Index loops** (§20, weak alone): `for (let i = 0; i < xs.length; i++) { const x = xs[i]; … }` becomes `for (const x of xs)` when `xs` is an array, `i` has no other use, and the body never reassigns `xs`. Not on strings: `for…of` walks code points, the index loop UTF-16 units.
- **`'use strict'` in modules** (§21, weak alone): in `.mjs` files or under `"type": "module"`. Remove it only if the built output is still an ES module.
- **Emoji and step logs** (§4, §22): `console.log('🚀 Server running on port ' + PORT)`. Strong in comments, medium in Node CLI logs, where emoji progress logs predate AI. Scripts parse CLI stdout, so apply §22's conditions.
- **Aliases and barrels for nothing** (§15, medium): `export const fetchUserData = getUserById;`, or an `index.ts` re-exporting one file. Remove only when nothing in the repo imports it and no `package.json` entry point (`main`, `module`, `exports`, `types`, `bin`) reaches it, directly or through re-exports.

## What people write instead

- `x == null` for "null or undefined", often the file's only loose equality.
- `catch {}` without a binding when the error is unused.
- Guard clauses; `for…of` with `await` for ordered steps, `Promise.all` for parallel work.
- Types on parameters, exported signatures and empty collections; inference elsewhere.
- In services, one logger (pino, winston, `debug` namespaces) with fields. In CLIs, `console.log` for output and `console.error` for problems.

## Comments that do things

- TypeScript: `// @ts-ignore`, `// @ts-expect-error`, `// @ts-nocheck` and `// @ts-check` (both only in the comments before the first statement), `/// <reference path|types|lib />` and `/// <amd-module />` (only above all code).
- JSDoc in checked JS, or JS that `.d.ts` files are built from: `@type`, `@param`, `@returns`, `@typedef`, `@callback`, `@template`, `@satisfies`, `@import`, `@enum`, `@override`. Anywhere: `@deprecated`, `@internal`, and API Extractor's `@public`, `@beta`, `@alpha`.
- Lint and format: `eslint-disable`, `eslint-disable-line`, `eslint-disable-next-line`, `eslint-enable`, `/* eslint rule: … */`, `/* eslint-env */`, `/* global */`, `/* exported */`, `// prettier-ignore`, `// biome-ignore`, `// deno-lint-ignore`, `// oxlint-disable`, `// tslint:disable`, `/* jshint */`, `// $FlowFixMe`.
- Coverage: `istanbul ignore`, `c8 ignore`, `v8 ignore`.
- Test runners: `/** @jest-environment jsdom */` and `// @vitest-environment` at the top of a test file.
- Bundlers: webpack magic comments (`webpackChunkName`, `webpackIgnore`, `webpackPrefetch`), `/* @vite-ignore */`, `/*#__PURE__*/`, `/* @__PURE__ */`, `/* @__NO_SIDE_EFFECTS__ */`, `//# sourceMappingURL=`, `//# sourceURL=`.
- Pragmas: `@jsx`, `@jsxFrag`, `@jsxImportSource`, `@jsxRuntime`, `// @flow`.
- Generator input: swagger-jsdoc `@swagger` and `@openapi`, `/* @ngInject */`, gettext `/* translators: */`.
- Headers: the `#!/usr/bin/env node` shebang, `@generated`, and legal comments (`/*!`, `//!`, `@license`, `@preserve`), which esbuild keeps (https://esbuild.github.io/api/#legal-comments); `tsc --removeComments` keeps only the `/*!` form.
- Directive prologues, which are strings: `'use strict'`, `'use client'`, `'use server'`.

## Looks cosmetic, isn't

- **Removing `'use strict'` from code that runs as CommonJS.** `function who() { return this; }` then returns `globalThis` instead of `undefined`, and assigning an undeclared name creates a global instead of throwing. Check the output: tsc adds the directive to every module it emits as CommonJS, but esbuild converts an ESM file to CommonJS without it, unless the file is .ts and tsconfig sets `strict` or `alwaysStrict`.
- **Removing the last `import` or `export`, including `export {};`.** TypeScript then treats the file as a global script: `declare global` fails with TS2669, and tsc stops emitting `"use strict"` unless `alwaysStrict` is on (`strict` turns it on). Neither happens when `moduleDetection` is `"force"`, or when `module` is `node16` or `nodenext` in a `"type": "module"` package. Node runs a `.js` file with no `"type"` field as CommonJS once it has no ESM syntax, so the file is no longer strict and top-level `this` and `require` change (https://nodejs.org/api/packages.html#syntax-detection).
- **Removing the last value use of an import.** tsc and esbuild drop imports used only as types. Delete an "impossible" `instanceof LegacyUser` guard and `./legacy` no longer loads or registers anything. Switching to `import type` also drops the import. `verbatimModuleSyntax` in tsconfig makes both keep plain imports.
- **Barrel to deep import.** `import { a } from './lib'` evaluates every module the barrel re-exports; `./lib/a` evaluates one, so the others' side effects stop. `export *` never re-exports a default.
- **Moving `require()` to the top.** Inside a function it loads on first call; at the top, at startup. An optional dependency that only one function requires then crashes startup when it is not installed. ESM imports run before the file's own code wherever they sit.
- **A comment between a directive and its target.** `@ts-ignore` and `@ts-expect-error` skip blank and `//` lines but stop at a `/* */` or JSDoc block, and the error returns. `eslint-disable-next-line` covers only the next line (https://eslint.org/docs/latest/use/configure/rules#disable-rules). `// @ts-check` after a statement and `/// <reference>` below code are plain comments.
- **Changing a type on a decorated class.** Under `emitDecoratorMetadata`, `constructor(private svc: UserService)` emits `UserService` in `design:paramtypes`; an interface type emits `Object`. Removing `: number` from a decorated property changes its `design:type` from `Number` to `Object`. Code reading reflect-metadata sees the change.
- **Reordering numeric enum members.** In `enum Color { Red, Green }`, `Red` is 0; swap them and it is 1, so stored values change meaning.
- **`private` to `#private`.** `JSON.stringify` and `Object.keys` include a `private` field and skip a `#` field.
- **`typeof x === 'undefined'` to `x === undefined`.** The second throws ReferenceError for an undeclared global, such as `window` in Node.
- **`forEach` to `for…of`.** `return` in a `forEach` callback skips one item; in `for…of` it leaves the function. `for…of` visits array holes that `forEach` skips. `forEach` stops at the length the array had when it started; `for…of` also visits items pushed during the loop. `for…in` on an array yields string keys plus extra enumerable properties.
- **Merging object literals.** Property order is insertion order, except integer-like keys (`'1'`, `'200'`), which always come first in ascending order: `{ 'x-b': 1, '200': 2 }` has keys `['200', 'x-b']`. `Object.keys`, `JSON.stringify` and `res.writeHead(status, headers)` all see that order. In a spread, the later object wins: `{ ...base, ...headers }` lets the caller override `base`, the reverse does not.
- **Lookup tables.** `table[key]` also finds inherited names: `({ ECONNRESET: 400 })['constructor']` is a function, not `undefined`. Object keys are strings, so `Object.hasOwn(REASONS, status)` matches `'404'` and `[404]` where the `===` ladder matched only `404`; a `Map` keeps `===` semantics. `REASONS.get(k) ?? 60` turns a branch that returned `null` into 60: test `map.has(k)` instead. A branch that built a fresh `{}` or `[]` must not become one shared table entry. A duplicate key keeps the ladder's first match but the object literal's last.
- **Merging into a loop.** A closure made in a `for (var k …)` loop sees the last `k`; use `let` or `const`.
- **Shared regex constants.** A `/g` or `/y` regex keeps `lastIndex` between `test()` calls, so one shared `const DIGITS = /^\d+$/g` gives `true` then `false` for two valid inputs.
- **Dropping `export`.** `import * as ns` sees every export, so `Object.keys(ns)` changes, and so does a dynamic `import()` that reads the name. A test that imports the name breaks. Frameworks read exports by name from outside the repo: Next.js route config (`revalidate`, `dynamic`, `runtime`, `generateStaticParams`), Storybook stories, Remix `loader` and `action`, SvelteKit `load`, Svelte `export let` props, a Lambda `handler` named in deploy config, and the names an IIFE bundle exposes through `--global-name`.
- **Log rewrites.** `console.log('user:', user)` prints the inspected object; `` console.log(`user: ${user}`) `` prints `[object Object]`. A first argument with `%d` or `%s` is a format string. `console.info` and `console.debug` go to stdout, `console.warn` and `console.error` to stderr.

## Safe modernizations

Syntax (`catch {}`, object spread, `??=`) needs the oldest runtime you support to have it, unless the compiler's `target` is older than the feature and rewrites it. Methods (`at`, `Object.hasOwn`, `includes`) always need the runtime to have them: tsc and esbuild do not polyfill, and `lib` only changes what type-checks.

- `x !== null && x !== undefined` → `x != null`: any version. Only the browser's `document.all` differs.
- `catch (err) {}` with `err` unused → `catch {}`: ES2019, TypeScript 2.5.
- `{ ...(x || {}) }` → `{ ...x }` in an object literal: ES2018.
- `const [x] = await Promise.all([p])` → `const x = await p`: any version, when nothing else reads the array and no code depends on microtask order (it settles one microtask sooner).
- `x ? x : y` → `x || y`: any version, when reading `x` has no side effects and gives the same value twice.
- `arr[arr.length - 1]` → `arr.at(-1)` on arrays and strings: ES2022.
- `Object.prototype.hasOwnProperty.call(o, k)` → `Object.hasOwn(o, k)`: ES2022.
- `s.indexOf(t) !== -1` → `s.includes(t)` when both are strings: ES2015.
- `x = x ?? y` → `x ??= y` for a local variable: ES2021. On a property, `??=` skips the setter.
- Removing `'use strict'`: only where the built output is an ES module, which is always strict (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode).

Not equivalent:

- `||`, `??` and default parameters: they differ for `0`, `''`, `false`, `NaN` and `null`.
- `a && a.b` → `a?.b` as a value: `0 && x` is `0`; `?.` gives `undefined`.
- `arr.indexOf(x) !== -1` → `arr.includes(x)`: `includes` finds `NaN` and reads holes as `undefined`.
- `substr` → `substring`; `parseInt(s)` → `parseInt(s, 10)` (`'0x1F'` gives 31 before, 0 after); `JSON.parse(JSON.stringify(x))` → `structuredClone(x)` (keeps Dates, throws on functions).
- `var` → `let`/`const`: scope, hoisting and loop closures change, and a classic script loses its global.
- `function` ↔ arrow: `this`, `arguments`, hoisting and `new` change. `.map(s => parseInt(s))` → `.map(parseInt)` passes the index as the radix: `['1', '2', '3']` gives `[1, NaN, NaN]`.
- `.then()` → `await`, and sequential `await` → `Promise.all`: timing, concurrency and caught errors change.
- `require` ↔ `import`: imports are hoisted, ESM lacks `require` and `__dirname`, and default interop differs.

## Verify

Baseline with the repo's scripts: `npx tsc --noEmit -p <each tsconfig>`, `npx eslint .`, `npm test` (for Jest, `npm test -- --ci`, so a new snapshot fails instead of being written), `npm run build`.

Comment-only pass: run `scripts/check_cosmetic.py`, then compare comment-stripped emit.

```sh
# once before editing into .hc/before, once after into .hc/after
npx tsc -p tsconfig.json --noEmit false --emitDeclarationOnly false --removeComments \
  --sourceMap false --inlineSourceMap false --declarationMap false \
  --incremental false --composite false --outDir .hc/before
diff -r .hc/before .hc/after
```

The extra flags make tsc write JavaScript even when tsconfig says not to, and keep source maps and build info, which change whenever a line moves, out of the diff. If tsc reports TS5096 (`allowImportingTsExtensions`), it still writes the files, so the diff is still valid. `npx esbuild <files> --outdir=.hc/before` works the same way. It also keeps legal comments, `/* @__PURE__ */` and the webpack and Vite comments inside `import()`, which `tsc --removeComments` drops (it keeps only the shebang and `/*!` comments); check other removed lines against the list above. Neither sees JSDoc type edits under `checkJs` (rerun `tsc --noEmit`) or a comment moved between a directive and its target (rerun tsc and ESLint).

Type-level edits: rerun the tsc command with `--declaration --emitDeclarationOnly` in place of `--emitDeclarationOnly false`, into new folders. Identical `.d.ts` files show that no exported name or type changed. They say nothing about runtime.

Rename pass: tsc catches a missed reference in TypeScript, ESLint's `no-undef` in JS. A new name that captures an outer variable or a global still compiles, so run `npx eslint --rule 'no-shadow: [error, {builtinGlobals: true}]' <files>` (`@typescript-eslint/no-shadow` in TS). `git diff --no-index --word-diff .hc/before .hc/after` on the stripped emit should show only old and new names, and `git grep -n '<old name>'` no string use. The emit diff and lint miss names that are data, which look like a clean rename: object shorthand (`{ user }` renames a key), `fn.name` in logs, `module.exports[name]`. Grep finds only the ones spelled as strings, such as `jest.spyOn(obj, 'name')`.
