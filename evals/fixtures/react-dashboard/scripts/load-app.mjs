import { build } from 'esbuild';
import { fileURLToPath, pathToFileURL } from 'node:url';

// bundles src/ for node so the tests render the real components
export async function loadApp(name) {
  const outfile = fileURLToPath(new URL(`../.cache/${name}.mjs`, import.meta.url));
  await build({
    entryPoints: [fileURLToPath(new URL('../src/index.ts', import.meta.url))],
    bundle: true,
    platform: 'node',
    format: 'esm',
    jsx: 'automatic',
    packages: 'external',
    outfile,
    logLevel: 'silent',
  });
  return import(pathToFileURL(outfile).href);
}
