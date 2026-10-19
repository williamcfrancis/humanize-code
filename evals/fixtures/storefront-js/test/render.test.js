import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { renderHomePage } from '../src/pages/home.js';
import { loadCartData, renderCartSummary } from '../src/components/CartSummary.js';

const fixtures = JSON.parse(readFileSync(new URL('../fixtures/api.json', import.meta.url), 'utf8'));
const snapshot = (name) => readFileSync(new URL(`./__snapshots__/${name}`, import.meta.url), 'utf8');

test('home page', async () => {
  const html = await renderHomePage({
    products: fixtures.products,
    apiClient: { getCart: async () => fixtures.cart },
  });
  assert.equal(html, snapshot('home.html'));
});

test('cart shows the error state when the API call fails', async () => {
  const cart = await loadCartData({ getCart: async () => { throw new Error('503'); } });
  assert.equal(renderCartSummary(cart), snapshot('cart-error.html'));
});

test('cart treats a null item list as empty', () => {
  assert.equal(renderCartSummary({ items: null }), snapshot('cart-empty.html'));
});

test('cart with a single item', () => {
  assert.equal(renderCartSummary({ items: [{ price: 5, quantity: 1 }] }), snapshot('cart-single.html'));
});
