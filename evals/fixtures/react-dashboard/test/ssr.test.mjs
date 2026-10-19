import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { loadApp } from '../scripts/load-app.mjs';

const { App } = await loadApp('ssr');
const fixture = (name) => JSON.parse(readFileSync(new URL(`../fixtures/${name}.json`, import.meta.url), 'utf8'));
const snapshot = (name) => readFileSync(new URL(`./__snapshots__/${name}`, import.meta.url), 'utf8');
const render = (data) => renderToStaticMarkup(createElement(App, { userId: 'u-1', initialData: data }));

test('dashboard', () => {
  assert.equal(render(fixture('dashboard')), snapshot('dashboard.html'));
});

test('empty account', () => {
  assert.equal(render(fixture('empty')), snapshot('empty.html'));
});

test('error state', () => {
  assert.equal(render({ status: 'error', message: 'Service unavailable' }), snapshot('error.html'));
});

function readSources(dir) {
  return readdirSync(dir).map((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? readSources(path) : readFileSync(path, 'utf8');
  }).join('\n');
}

// Tailwind only generates classes it can find spelled out in full in the source files
test('every class used at runtime is spelled out in src/', () => {
  const html = [render(fixture('dashboard')), render(fixture('empty'))].join('');
  const used = new Set([...html.matchAll(/class="([^"]*)"/g)].flatMap((m) => m[1].split(/\s+/)).filter(Boolean));
  const source = readSources(fileURLToPath(new URL('../src', import.meta.url)));
  const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const missing = [...used].filter((c) => !new RegExp(`(^|[\\s'"\`])${escape(c)}([\\s'"\`]|$)`, 'm').test(source));
  assert.deepEqual(missing, []);
});
