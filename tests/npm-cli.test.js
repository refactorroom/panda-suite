'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const cli = path.join(root, 'bin/panda-suite.js');
test('CLI help and invalid arguments', () => {
  for (const [args, code] of [[['--help'], 0], [[], 1], [['install'], 1], [['install', '--all', '--skill', 'panda-plan'], 1], [['update', '--destination'], 1], [['update', '--all'], 1]]) {
    assert.equal(spawnSync(process.execPath, [cli, ...args], { encoding: 'utf8' }).status, code, args.join(' '));
  }
});
test('package and plugin versions agree', () => {
  assert.equal(require('../package.json').version, require('../plugin.json').version);
  assert.equal(require('../package.json').version, require('../.claude-plugin/plugin.json').version);
});
const fs = require('node:fs');
const os = require('node:os');
function fixture(t) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'panda-cli-'));
  t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));
  const pkg = path.join(tmp, 'package');
  fs.mkdirSync(pkg);
  fs.cpSync(path.join(root, 'bin'), path.join(pkg, 'bin'), { recursive: true });
  fs.copyFileSync(path.join(root, 'package.json'), path.join(pkg, 'package.json'));
  fs.writeFileSync(path.join(pkg, 'bin/packaged-files.json'), '{}');
  for (const name of ['panda-one', 'panda-two']) {
    const dir = path.join(pkg, 'skills', name); fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'SKILL.md'), `${name} v1`);
    fs.writeFileSync(path.join(dir, 'old.md'), 'old');
  }
  const dest = path.join(tmp, 'dest');
  const runWith = (env, ...args) => spawnSync(process.execPath, [path.join(pkg, 'bin/panda-suite.js'), ...args, '--destination', dest], { encoding: 'utf8', env: { ...process.env, ...env } });
  const run = (...args) => runWith({}, ...args);
  return { pkg, dest, run, runWith, tmp };
}
test('install tracks selected files and refuses collisions and unsafe inputs', t => {
  const { pkg, dest, run } = fixture(t);
  assert.equal(run('install', '--skill', 'panda-one', '--skill', 'panda-one').status, 0);
  const state = JSON.parse(fs.readFileSync(path.join(dest, '.panda-suite-state.json')));
  assert.deepEqual(Object.keys(state.skills), ['panda-one']);
  assert.deepEqual(Object.keys(state.skills['panda-one'].files).sort(), ['SKILL.md', 'old.md']);
  assert.match(state.skills['panda-one'].files['SKILL.md'], /^[a-f0-9]{64}$/);
  const before = fs.readFileSync(path.join(dest, '.panda-suite-state.json'), 'utf8');
  assert.notEqual(run('install', '--skill', '../bad').status, 0);
  assert.notEqual(run('install', '--skill', 'unknown').status, 0);
  assert.notEqual(run('install', '--all').status, 0);
  assert.equal(fs.existsSync(path.join(dest, 'panda-two')), false);
  assert.equal(fs.readFileSync(path.join(dest, '.panda-suite-state.json'), 'utf8'), before);
  fs.symlinkSync(path.join(pkg, 'package.json'), path.join(pkg, 'skills/panda-two/link'));
  assert.notEqual(run('install', '--skill', 'panda-two').status, 0);
});
test('update replaces full content and preserves missing upstream skills', t => {
  const { pkg, dest, run } = fixture(t);
  assert.equal(run('install', '--all').status, 0);
  fs.writeFileSync(path.join(pkg, 'skills/panda-one/SKILL.md'), 'v2');
  fs.rmSync(path.join(pkg, 'skills/panda-one/old.md'));
  fs.rmSync(path.join(pkg, 'skills/panda-two'), { recursive: true });
  const result = run('update'); assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /Skipped panda-two/);
  assert.equal(fs.readFileSync(path.join(dest, 'panda-one/SKILL.md'), 'utf8'), 'v2');
  const updatedState = JSON.parse(fs.readFileSync(path.join(dest, '.panda-suite-state.json')));
  assert.equal(updatedState.packageVersion, require('../package.json').version);
  assert.equal(updatedState.skills['panda-one'].files['SKILL.md'], require('node:crypto').createHash('sha256').update('v2').digest('hex'));
  assert.equal('old.md' in updatedState.skills['panda-one'].files, false);
  assert.equal(fs.existsSync(path.join(dest, 'panda-one/old.md')), false);
  assert.equal(fs.readFileSync(path.join(dest, 'panda-two/SKILL.md'), 'utf8'), 'panda-two v1');
  assert.equal(run('update').status, 0);
});
test('update refuses local changes and leaves all other data untouched', t => {
  for (const change of ['edited', 'added', 'deleted', 'symlink', 'missing']) {
    const { dest, run } = fixture(t);
    assert.equal(run('install', '--all').status, 0);
    const first = path.join(dest, 'panda-one'), statePath = path.join(dest, '.panda-suite-state.json');
    if (change === 'edited') fs.writeFileSync(path.join(first, 'old.md'), 'edited');
    if (change === 'added') fs.writeFileSync(path.join(first, 'extra'), 'extra');
    if (change === 'deleted') fs.rmSync(path.join(first, 'old.md'));
    if (change === 'symlink') fs.symlinkSync(path.join(dest, 'panda-two/SKILL.md'), path.join(first, 'link'));
    if (change === 'missing') fs.rmSync(first, { recursive: true });
    const before = fs.readFileSync(statePath, 'utf8');
    assert.notEqual(run('update').status, 0, change);
    assert.equal(fs.readFileSync(statePath, 'utf8'), before);
    assert.equal(fs.readFileSync(path.join(dest, 'panda-two/SKILL.md'), 'utf8'), 'panda-two v1');
  }
});
test('corrupt state, locks and interrupted journal refuse writes', t => {
  const { dest, run } = fixture(t);
  assert.notEqual(run('update').status, 0);
  assert.equal(run('install', '--all').status, 0);
  fs.mkdirSync(path.join(dest, '.panda-suite-lock'));
  assert.notEqual(run('update').status, 0);
  fs.rmSync(path.join(dest, '.panda-suite-lock'), { recursive: true });
  fs.mkdirSync(path.join(dest, '.panda-suite-transaction'));
  assert.notEqual(run('update').status, 0);
  fs.rmSync(path.join(dest, '.panda-suite-transaction'), { recursive: true });
  fs.writeFileSync(path.join(dest, '.panda-suite-state.json'), '{broken');
  assert.notEqual(run('update').status, 0);
  assert.equal(fs.readFileSync(path.join(dest, 'panda-one/SKILL.md'), 'utf8'), 'panda-one v1');
});
test('failure during replacement or state commit restores earlier data', t => {
  for (const point of ['second', 'state']) {
    const { pkg, dest, run, runWith, tmp } = fixture(t);
    assert.equal(run('install', '--all').status, 0);
    const statePath = path.join(dest, '.panda-suite-state.json');
    const before = fs.readFileSync(statePath, 'utf8');
    for (const name of ['panda-one', 'panda-two']) fs.writeFileSync(path.join(pkg, 'skills', name, 'SKILL.md'), 'new');
    const hook = path.join(tmp, 'inject.cjs');
    fs.writeFileSync(hook, `const fs = require('fs'); const original = fs.renameSync; let thrown = false; fs.renameSync = function(a,b) { if (!thrown && (${point === 'state' ? "String(a).endsWith('state.after')" : "String(a).includes('/staged/panda-two')"})) { thrown = true; throw new Error('injected failure'); } return original.apply(this, arguments); };`);
    const result = runWith({ NODE_OPTIONS: `--require=${hook}` }, 'update');
    assert.notEqual(result.status, 0, point); assert.match(result.stderr, /injected failure/);
    assert.equal(fs.readFileSync(statePath, 'utf8'), before);
    assert.equal(fs.readFileSync(path.join(dest, 'panda-one/SKILL.md'), 'utf8'), 'panda-one v1');
    assert.equal(fs.readFileSync(path.join(dest, 'panda-two/SKILL.md'), 'utf8'), 'panda-two v1');
    assert.equal(fs.existsSync(path.join(dest, '.panda-suite-transaction')), false);
  }
});

test('packaged omitted files match source bytes', () => {
  for (const [name, encoded] of Object.entries(require('../bin/packaged-files.json'))) assert.deepEqual(Buffer.from(encoded, 'base64'), fs.readFileSync(path.join(root, name)));
});
test('staging errors and late collisions leave existing files untouched', t => {
  for (const point of ['stage', 'collision']) {
    const { dest, runWith, tmp } = fixture(t);
    const hook = path.join(tmp, 'inject.cjs');
    const inject = point === 'stage'
      ? `const original=fs.cpSync; fs.cpSync=function(a,b) { if (String(b).includes('/staged/')) throw Error('injected stage error'); return original.apply(this,arguments); };`
      : `const original=fs.mkdirSync; let done=false; fs.mkdirSync=function(a,...rest) { if (!done && String(a).endsWith('/dest/panda-one')) { done=true; original.call(this,a,...rest); fs.writeFileSync(String(a)+'/user.txt','keep'); } return original.call(this,a,...rest); };`;
    fs.writeFileSync(hook, `const fs=require('fs'); ${inject}`);
    assert.notEqual(runWith({ NODE_OPTIONS: `--require=${hook}` }, 'install', '--skill', 'panda-one').status, 0);
    assert.equal(fs.existsSync(path.join(dest, '.panda-suite-state.json')), false);
    if (point === 'collision') assert.equal(fs.readFileSync(path.join(dest, 'panda-one/user.txt'), 'utf8'), 'keep');
    else assert.equal(fs.existsSync(path.join(dest, 'panda-one')), false);
  }
});
