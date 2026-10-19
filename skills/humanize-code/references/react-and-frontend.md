# React and frontend: humanize-code reference

Read this with SKILL.md before editing React, Next.js, Vue, Svelte, Angular, HTML, or CSS beyond comments. Here behavior means the DOM, the pixels, and the accessibility tree.

## Tells

- **Label comments in markup** (§8, weak alone; medium in JSX when `{/* Header */}` labels `<Header />` on every block). Delete a JSX comment only when it is a whole child on its own lines, not between two lines of text. Svelte strips template comments unless `preserveComments` is set. Vue strips them only in production builds without `compilerOptions.comments`; dev builds and tests render them as DOM comments ([Vue](https://vuejs.org/api/application.html#app-config-compileroptions-comments)), so a component snapshot can change. In HTML and server templates a comment is a DOM node: report it.
- **Effect narration** (§5, medium): `// Fetch data on mount` above `useEffect`. Delete the comment, keep the effect. Moving derived state into render changes the first paint and SSR HTML: report that.
- **Prop docs that restate types** (§6, medium): `@param {Props} props - The props`, `@returns {JSX.Element}`. Delete in `.ts` and `.tsx`. Keep them in `checkJs` and `// @ts-check` files, where Storybook or react-docgen publish them, and when they carry units, ranges, `@deprecated`, `@default`, or `@example`.
- **Noise memoization** (§20, weak alone). Remove a `useMemo` or `useCallback` only when its value goes only to text or to props of built-in DOM elements (not a custom element, a `ref` prop or ref object, a child component, a dependency array, context, a hook return, or `===`), it is not JSX, its callback is cheap and has no side effects, its deps are complete, and React Compiler is off. A new function each render makes React detach and reattach a `ref` callback ([react.dev](https://react.dev/reference/react-dom/components/common#ref-callback)) and set a custom element's property again. Never remove `React.memo`.
  ```tsx
  const [open, setOpen] = useState(false);
  const onClick = useCallback(() => setOpen(true), []);
  const title = useMemo(() => `Hello, ${name}`, [name]);
  return <button onClick={onClick}>{title}</button>;
  ```
  ```tsx
  const [open, setOpen] = useState(false);
  return <button onClick={() => setOpen(true)}>{`Hello, ${name}`}</button>;
  ```
- **Redundant ARIA** (§20, report only): `role="button"` on `<button>`, `aria-required` beside `required`. Tests may read those attributes, and `aria-label` can change the accessible name.
- **Stale idioms** (§21, report only, except the [safe modernizations](#safe-modernizations)): `React.FC`, an unused `import React`, `'use client'` on a page with no state, `forwardRef` in React 19, NgModules in a standalone Angular app.
- **Duplicate utilities** (§20, weak alone): `cn('flex items-center flex')`. Inside `twMerge`, or a `cn` that calls it, when both copies sit in the same unconditional string, delete the earlier copy only if `twMerge` already drops it: it keeps the last copy of a Tailwind class but every copy of a class it does not recognize (`twMerge('card p-4 card')` returns all three). A `cn` built on `clsx` alone, or a plain `className`, keeps both copies, so the attribute text would change: report it. Never touch a conflict like `text-sm text-base`.

## What people write instead

- Props destructured with defaults in the signature, `function Card({ size = 'md' })`, and `export default function Page()` in Next.js.
- Inline one-line handlers; a named `handleSubmit` only for a long body.
- `count > 0 && <List />`, or a ternary with `null`, for numbers.
- Class variants as maps of full literal strings, joined with the repo's `cn()` or `clsx`.
- Rare JSX comments that name a browser bug or a third-party constraint.

## Comments that do things

- **JSX and TS:** `{/* @ts-expect-error */}`, `{/* eslint-disable-next-line */}`, `biome-ignore`, `prettier-ignore`, `@jsx`, `@jsxFrag`, `@jsxRuntime`, `@jsxImportSource`, `// @refresh reset`, `@jest-environment`, `@vitest-environment`, `istanbul ignore`, `c8 ignore`, `v8 ignore`, `/// <reference types="vite/client" />`.
- **Directive strings:** `'use client'`, `'use server'`, `'use cache'`, `'use memo'`, `'use no memo'`, `'use strict'`, `'ngInject'`, and `/* @ngInject */`.
- **Bundler:** `webpackChunkName`, `webpackPrefetch`, `webpackPreload`, `webpackMode`, `webpackIgnore` (also before a CSS `@import` or `url()`), `@vite-ignore`, `#__PURE__`, `@__NO_SIDE_EFFECTS__`, `sourceMappingURL`.
- **Tailwind:** any comment in a scanned file that spells out class names. Tailwind reads files as plain text, so deleting the only mention of `bg-red-500` drops its rule.
- **CSS:** `/*!`, `stylelint-disable`, `prettier-ignore`, the `purgecss` ignore comments, RTLCSS `rtl:` directives, CSSJanus `@noflip`, `autoprefixer: off`, `autoprefixer: ignore next`.
- **Templates:** `<!-- eslint-disable-next-line -->`, `<!-- prettier-ignore -->`, `<!-- @vue-ignore -->`, `<!-- @vue-expect-error -->`, `<!-- @vue-skip -->`, and `<!-- svelte-ignore -->` directly above its target.
- **HTML:** `<!-- ko -->`, `<!--#include -->`, `<!--[if mso]>`, downlevel-revealed `<!--[if !IE]><!-->`, `<!--` `-->` pairs joining inline-block items, and `build:`, `inject:`, and `htmlmin:ignore` markers.

## Looks cosmetic, isn't

Claims without a link were run on React 19.3 (and 18.3 for `defaultProps`), Vue 3.5, Svelte 5.57, and Tailwind 4.3.

- **A ternary split into two `&&`.** `{a ? <Field /> : <Field />}` keeps the field's state when `a` flips; `{a && <Field />}{!a && <Field />}` resets it ([react.dev](https://react.dev/learn/preserving-and-resetting-state)).
- **Wrappers.** Replacing a wrapper `div` with a Fragment changes the DOM, `.row > button` selectors, and layout. A wrapper that differs between branches (`a ? <div><Field /></div> : <Field />`) remounts `Field` and resets its state.
- **Keys.** A `key` on a single element resets it on purpose. With `key={index}`, removing a row leaves its typed input in the row that moves into its place; with `key={id}` the input leaves with its row. Switching between them changes what users see.
- **An early return above a hook** throws ("Rendered fewer hooks than expected") when another hook runs before it. When none does, the state below it silently resets each time it fires.
- **Effects.** Deleting a cleanup that looks redundant leaves the subscription or timer running after a dependency change, after unmount, and through Strict Mode's extra development setup ([react.dev](https://react.dev/reference/react/useEffect)). `useLayoutEffect` to `useEffect` lets the browser paint first, so the element can flicker ([react.dev](https://react.dev/reference/react/useLayoutEffect)).
- **Handlers.** `onClick={handle}` passes the event; `onClick={() => handle()}` does not.
- **Attribute text.** `title="a &amp; b"` decodes the entity; `title={"a &amp; b"}` does not. `className={''}` renders `class=""` and `undefined` renders nothing. `` `btn ${x ? 'on' : ''}` `` leaves a trailing space that `clsx` would drop. `marginTop: 0` renders `margin-top:0`, `'0px'` renders `0px`.
- **Elements.** Without `type="button"`, a button in a `<form>` submits it ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button)). A `<div>` inside a `<p>` breaks hydration ([Next.js](https://nextjs.org/docs/messages/react-hydration-error)).
- **Rest props.** Dropping an unused `variant` from `{ variant, ...rest }` silently forwards `variant="primary"` to the DOM.
- **`defaultProps`.** React 19 ignores it on function components (`Btn.defaultProps = { size: 'md' }` renders `btn-undefined`), so converting it to `{ size = 'md' }` changes output. React 18 copies `defaultProps` into the element's props, so the two differ whenever code reads the props object (`props.size`, `{...props}`) or a parent inspects the element (`Children.map`, `cloneElement`).
- **Hydration guards.** A mounted-flag effect is Next.js's documented hydration fix, and a `typeof window` check in render logic is a listed cause of hydration errors ([Next.js](https://nextjs.org/docs/messages/react-hydration-error)).
- **Next.js.** `page` and `layout` files need a default export ([docs](https://nextjs.org/docs/app/api-reference/file-conventions/page)), and `React.lazy` needs a module whose `.default` is the component ([react.dev](https://react.dev/reference/react/lazy)). Without Cache Components, `revalidate = 600` works and `60 * 10` does not ([docs](https://nextjs.org/docs/app/guides/caching-without-cache-components)). `metadata` and `generateMetadata` cannot share a segment ([docs](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)). `'use client'` precedes all imports ([docs](https://nextjs.org/docs/app/api-reference/directives/use-client)), and `error.tsx` must be a Client Component ([docs](https://nextjs.org/docs/app/api-reference/file-conventions/error)).
- **Template whitespace.** Vue's default `condense` removes whitespace that contains a newline between elements, so wrapping `<b>a</b> <i>b</i>` onto two lines removes the gap ([Vue](https://vuejs.org/api/application.html)). Svelte keeps one space. Angular removes whitespace between elements by default ([Angular](https://angular.dev/guide/templates/whitespace)).
- **Vue.** Destructuring `reactive()` loses reactivity. `watch(foo)` on a destructured prop does not compile in 3.5; it needs `() => foo`. `v-if` on a `v-for` element runs first, so it cannot see the loop variable ([Vue](https://vuejs.org/guide/essentials/list.html)). Dropping `:deep()` or `scoped` changes what a rule matches.
- **Svelte 4 syntax.** `items = items` after `push` triggers the update. `$:` tracks only names it references, so moving its expression into a helper stops updates. One added rune switches the component to runes mode, and `$:` stops compiling.
- **Angular.** `inject()` outside an injection context throws NG0203 ([DI context](https://angular.dev/guide/di/dependency-injection-context)). `@Input()` to `input()` gives read-only signals that tests cannot assign ([Angular](https://angular.dev/guide/components/inputs)). Since v22, OnPush is the default ([Angular](https://angular.dev/api/core/Component)), so deleting an explicit `ChangeDetectionStrategy.Eager` or `Default` changes when the view updates; before v22, deleting `OnPush` does.
- **Tailwind.** `class="grid flex"` is `display: grid`: stylesheet order decides. In `twMerge` the last conflicting class wins ([tailwind-merge](https://github.com/dcastil/tailwind-merge/blob/main/packages/tailwind-merge/docs/features.md)), so sorting `cn()` arguments can change pixels. `_` in an arbitrary value is a space. `w-[327px]` to `w-80` is 320px at the default spacing. Tailwind 4 does not scan gitignored or CSS files ([Tailwind](https://tailwindcss.com/docs/detecting-classes-in-source-files)).
- **CSS Modules.** `styles.myClass` versus `styles['my-class']` depends on `exportLocalsConvention` ([css-loader](https://github.com/webpack/css-loader)). The wrong key is `undefined`, and the class vanishes.
- **styled-components.** `$variant` to `variant` forwards the prop ([docs](https://styled-components.com/docs/api#transient-props)): to a wrapped component in any version, and to the DOM in v6, which no longer filters props by default ([FAQ](https://styled-components.com/docs/faqs)).
- **Plain CSS.** `height: 100vh; height: 100dvh;` is a fallback, not a duplicate ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_syntax/Error_handling)). In a merged selector list, one unsupported selector voids the rule ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Selector_list)). Moving a declaration into or out of a `@layer`, an inline style, or `!important` changes which one wins ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Cascade)).
- **Accessibility.** `aria-label` overrides `alt` and `<label>` as the accessible name ([MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-label)). `alt=""` marks an image decorative; without `alt`, some screen readers read the file name ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img)). Renaming an `id` breaks the `htmlFor` and `aria-describedby` that point to it.

## Safe modernizations

- `const Card: React.FC<CardProps> = ({ title }) => …` to `function Card({ title }: CardProps) { … }`. Types are erased, so the runtime is identical. The type check must still pass: with @types/react before 18, `React.FC` also added an implicit `children` prop, so callers that pass children need it in `CardProps`. Leave it as a `const` arrow when it is wrapped (`memo`, `forwardRef`) or assigned conditionally.
- Delete `import React from 'react'` when the build uses the automatic JSX runtime (tsconfig `react-jsx`, Babel or SWC `runtime: 'automatic'`), the file has no other `React.` use and no JSX pragma, and nothing re-exports it.
- `<React.Fragment>` to `<>` when it has no `key` or other prop, the file has no JSX pragma, and the build sets no custom fragment (`jsxFragmentFactory`, Babel `pragmaFrag`, esbuild `jsxFragment`) and no non-React `jsxImportSource`.
- `<Ctx.Provider value={v}>` to `<Ctx value={v}>` on React 19 and later, when `Ctx` comes from React's `createContext` ([react.dev](https://react.dev/reference/react/createContext)).

Not equivalent:

- `defaultProps` to default parameters, as above.
- `forwardRef` to a `ref` prop on React 19: `ref` then arrives in `props`, so `{...rest}` passes it on.
- `ReactDOM.render` to `createRoot`: it turns on automatic batching ([react.dev](https://react.dev/blog/2022/03/08/react-18-upgrade-guide)).
- Removing `'use client'` from a file without hooks: it may be the client boundary for what it imports.
- Options API to `<script setup>`, Svelte 4 syntax to runes, `*ngIf` to `@if`: these are migrations. Report them.

## Verify

Check out the base commit in a `git worktree` to build both sides.

- **Comment-only pass:** `python scripts/check_cosmetic.py` compiles JS and TS with esbuild, so it catches a deleted JSX comment that changed spacing. It misses class names deleted from comments and directives outside its own list (`@refresh reset`, `@vitest-environment`, `v8 ignore`, `biome-ignore`, `@__NO_SIDE_EFFECTS__`, `@noflip`), so check those by hand. It skips `.vue`, `.svelte`, `.html`, and `.astro`; for those, build both trees and `diff -r` the output, after building the base twice to see what differs on its own.
- **Built CSS:** `cmp` the output of `npx @tailwindcss/cli -i src/app.css -o out.css` (v3: `npx tailwindcss`) from each tree, or the `sha256sum` of every built `.css`. Runtime CSS-in-JS is not covered.
- **SSR markup:** diff `renderToStaticMarkup` (or `vue/server-renderer`) output for each page with fixture props. It misses effects, client state, and hydration.
- **Browser:** run this against both builds, then `diff -r before after`. Run it twice on the base first to confirm it is stable. It needs Playwright 1.49 or later for `ariaSnapshot`; its calls match the Playwright docs, but it has not been run.
  ```js
  // node snap.mjs http://localhost:4173 before
  import { chromium } from 'playwright';
  import { mkdirSync, writeFileSync } from 'node:fs';
  const [base, out] = process.argv.slice(2);
  const routes = ['/', '/settings']; // every page and state that matters
  mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  for (const width of [1280, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    for (const r of routes) {
      await page.goto(base + r, { waitUntil: 'networkidle' });
      const f = `${out}/${width}${r.replaceAll('/', '_')}`;
      writeFileSync(`${f}.html`, await page.content());
      writeFileSync(`${f}.aria.yml`, await page.locator('body').ariaSnapshot());
      await page.screenshot({ path: `${f}.png`, fullPage: true, animations: 'disabled', caret: 'hide' });
    }
  }
  await browser.close();
  ```
  It sees only the states you load; loading, empty, and error states need their own routes or mocked responses.
- **Rename pass:** `npx tsc --noEmit`, `npx eslint .` with the `react-hooks` rules, `vue-tsc --noEmit`, `svelte-check`, or `ng build`, then the tests and the browser diff. Type checks catch a renamed shorthand key like `{ userData }` only when the object has a declared type.
