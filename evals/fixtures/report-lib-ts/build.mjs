import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { build } from 'esbuild';

// strips comments (keeps /*! ... */) and collapses whitespace
function minifyCss(css) {
  return css
    .replace(/\/\*(?!!)[\s\S]*?\*\//g, '')
    .replace(/\s+/g, ' ')
    .replace(/\s*([{}:;,])\s*/g, '$1')
    .replace(/;}/g, '}')
    .trim();
}

await mkdir(new URL('./dist/', import.meta.url), { recursive: true });
await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  platform: 'node',
  format: 'esm',
  outfile: 'dist/report-lib.mjs',
  logLevel: 'silent',
});
const css = await readFile(new URL('./src/styles/report.css', import.meta.url), 'utf8');
await writeFile(new URL('./dist/report.css', import.meta.url), minifyCss(css));
console.log('built dist/report-lib.mjs and dist/report.css');
