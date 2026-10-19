import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!doctype html><html><body></body></html>', { url: 'http://localhost/' });
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
const storage = dom.window.localStorage;

const { act, createElement } = await import('react');
const { createRoot } = await import('react-dom/client');
const { loadApp } = await import('../scripts/load-app.mjs');
const { App } = await loadApp('client');

const fixture = (name) => JSON.parse(readFileSync(new URL(`../fixtures/${name}.json`, import.meta.url), 'utf8'));
const snapshot = (name) => readFileSync(new URL(`./__snapshots__/${name}`, import.meta.url), 'utf8');
const settle = () => act(() => new Promise((resolve) => setTimeout(resolve, 30)));
const click = (el) => act(() => { el.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true })); });

async function mount(props) {
  const container = document.createElement('div');
  document.body.append(container);
  const root = createRoot(container);
  await act(() => { root.render(createElement(App, { userId: 'u-1', ...props })); });
  await settle();
  return {
    container,
    unmount: () => act(() => { root.unmount(); }).then(() => container.remove()),
  };
}

test('fetches once and does not refetch when unrelated state changes', { timeout: 10_000 }, async () => {
  storage.clear();
  const calls = [];
  const api = { getStats: async (query) => { calls.push(query); return fixture('empty'); } };
  const app = await mount({ api });
  try {
    assert.deepEqual(calls, [{ userId: 'u-1', range: '30d' }]);
    await click(app.container.querySelector('button[aria-expanded]'));
    await settle();
    assert.equal(calls.length, 1);
    assert.equal(app.container.innerHTML, snapshot('client-notifications.html'));
  } finally {
    await app.unmount();
  }
});

test('remembers the selected range', { timeout: 10_000 }, async () => {
  storage.clear();
  const calls = [];
  const api = { getStats: async (query) => { calls.push(query.range); return fixture('dashboard'); } };
  const first = await mount({ api });
  try {
    const sevenDays = [...first.container.querySelectorAll('button')].find((b) => b.textContent === '7d');
    await click(sevenDays);
    await settle();
    assert.deepEqual(calls, ['30d', '7d']);
    assert.equal(storage.getItem('dashboard-range'), '"7d"');
  } finally {
    await first.unmount();
  }
  const second = await mount({ api });
  try {
    assert.deepEqual(calls, ['30d', '7d', '7d']);
  } finally {
    await second.unmount();
  }
});

test('shows the API error message', { timeout: 10_000 }, async () => {
  storage.clear();
  const api = { getStats: async () => { throw new Error('Network down'); } };
  const app = await mount({ api });
  try {
    assert.equal(app.container.innerHTML, snapshot('client-error.html'));
  } finally {
    await app.unmount();
  }
});
