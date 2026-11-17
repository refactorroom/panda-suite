'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { checkForUpdate } = require('../bin/update-notice');

test('offers the latest release and forwards the original CLI arguments on acceptance', async () => {
  const calls = [];
  const handled = await checkForUpdate({ interactive: true, current: '1.8.0', args: ['install', '--all'], latest: async () => '1.9.0', ask: async version => { calls.push(version); return true; }, launch: (version, args) => { calls.push([version, args]); return 7; } });
  assert.deepEqual(calls, ['1.9.0', ['1.9.0', ['install', '--all']]]);
  assert.equal(handled, 7);
});

test('continues locally when declined, current, offline, or noninteractive', async () => {
  let asked = 0;
  const base = { interactive: true, current: '1.8.0', args: ['update'], latest: async () => '1.9.0', ask: async () => { asked++; return false; }, launch: () => { throw Error('must not launch'); } };
  assert.equal(await checkForUpdate(base), null);
  assert.equal(await checkForUpdate({ ...base, latest: async () => '1.8.0' }), null);
  assert.equal(await checkForUpdate({ ...base, latest: async () => { throw Error('offline'); } }), null);
  assert.equal(await checkForUpdate({ ...base, interactive: false, latest: async () => { throw Error('must not check'); } }), null);
  assert.equal(asked, 1);
});

test('CLI accepts an update and runs the newer package with the same arguments', () => {
  const fs = require('node:fs');
  const os = require('node:os');
  const path = require('node:path');
  const { spawnSync } = require('node:child_process');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'panda-update-test-'));
  try {
    const preload = path.join(tmp, 'preload.js');
    const calls = path.join(tmp, 'calls.json');
    fs.writeFileSync(preload, `
      const { EventEmitter } = require('node:events');
      Object.defineProperty(process.stdin, 'isTTY', { value: true });
      Object.defineProperty(process.stderr, 'isTTY', { value: true });
      require('node:https').get = (url, options, callback) => {
        const req = new EventEmitter(); req.setTimeout = () => {}; req.destroy = error => req.emit('error', error);
        process.nextTick(() => { const res = new EventEmitter(); res.statusCode = 200; res.setEncoding = () => {}; callback(res); res.emit('data', '{"version":"99.0.0"}'); res.emit('end'); });
        return req;
      };
      require('node:child_process').spawnSync = (command, args, options) => {
        require('node:fs').writeFileSync(${JSON.stringify(calls)}, JSON.stringify({command, args, skip: options.env.PANDA_SUITE_SKIP_UPDATE_CHECK}));
        return { status: 0 };
      };
    `);
    const cli = path.join(__dirname, '../bin/panda-suite.js');
    const result = spawnSync(process.execPath, ['--require', preload, cli, 'update', '--destination', path.join(tmp, 'dest')], { input: 'y\n', encoding: 'utf8', env: { ...process.env, CI: '', PANDA_SUITE_SKIP_UPDATE_CHECK: '' } });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stderr, /99\.0\.0/);
    const invoked = JSON.parse(fs.readFileSync(calls, 'utf8'));
    assert.deepEqual(invoked.args, ['--yes', 'panda-suite@99.0.0', 'update', '--destination', path.join(tmp, 'dest')]);
    assert.equal(invoked.skip, '1');
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});
