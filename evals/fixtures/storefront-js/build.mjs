import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { renderHomePage } from './src/pages/home.js';

const fixtures = JSON.parse(await readFile(new URL('./fixtures/api.json', import.meta.url), 'utf8'));

// strips comments (keeps /*! ... */) and collapses whitespace
function minifyCss(css) {
  return css
    .replace(/\/\*(?!!)[\s\S]*?\*\//g, '')
    .replace(/\s+/g, ' ')
    .replace(/\s*([{}:;,])\s*/g, '$1')
    .replace(/;}/g, '}')
    .trim();
}

const apiClient = { getCart: async () => fixtures.cart };

await mkdir(new URL('./dist/', import.meta.url), { recursive: true });
await writeFile(
  new URL('./dist/index.html', import.meta.url),
  await renderHomePage({ products: fixtures.products, apiClient }),
);
const css = await readFile(new URL('./src/styles/main.css', import.meta.url), 'utf8');
await writeFile(new URL('./dist/main.css', import.meta.url), minifyCss(css));
console.log('built dist/index.html and dist/main.css');
