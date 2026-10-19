import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { build } from 'esbuild';

const outfile = fileURLToPath(new URL('../.cache/report-lib.mjs', import.meta.url));
await build({
  entryPoints: [fileURLToPath(new URL('../src/index.ts', import.meta.url))],
  bundle: true,
  platform: 'node',
  format: 'esm',
  outfile,
  logLevel: 'silent',
});
const lib = await import(pathToFileURL(outfile).href);
const users = JSON.parse(readFileSync(new URL('../fixtures/users.json', import.meta.url), 'utf8'));
const expected = JSON.parse(readFileSync(new URL('./__snapshots__/report.json', import.meta.url), 'utf8'));

test('user summary', () => {
  assert.equal(JSON.stringify(lib.buildUserSummary(users)), expected.summary);
});

test('active user ids', () => {
  assert.deepEqual(lib.collectActiveUserIds(users), expected.activeIds);
});

test('flag masks', () => {
  assert.deepEqual(['0x1F', '12', '', undefined, '0x10'].map((v) => lib.parseFlagMask(v)), expected.masks);
});

test('exports', () => {
  assert.equal(lib.exportUsers(users, { format: 'csv' }), expected.csv);
  assert.equal(lib.exportUsers(users, { format: 'csv', includeDebugInfo: true }), expected.csvDebug);
  assert.equal(lib.exportUsers(users, { format: 'json', includeDebugInfo: false }), expected.json);
  assert.equal(lib.exportUsers(users, { format: 'legacy-csv' }), expected.legacyCsv);
  assert.throws(() => lib.exportUsers(users, { format: 'xml' }), { message: expected.unknownFormatError });
});
