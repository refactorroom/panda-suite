'use strict';
const https = require('node:https');
const readline = require('node:readline');
const { spawnSync } = require('node:child_process');

function newer(latest, current) {
  const next = /^(\d+)\.(\d+)\.(\d+)$/.exec(latest);
  const installed = /^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$/.exec(current);
  if (!next || !installed) return false;
  for (let i = 1; i <= 3; i++) {
    const difference = BigInt(next[i]) - BigInt(installed[i]);
    if (difference !== 0n) return difference > 0n;
  }
  return current.includes('-');
}

function latestVersion() {
  return new Promise((resolve, reject) => {
    const request = https.get('https://registry.npmjs.org/panda-suite/latest', { headers: { accept: 'application/json' } }, response => {
      if (response.statusCode !== 200) { response.resume(); reject(Error('Registry unavailable')); return; }
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { body += chunk; if (body.length > 1024 * 1024) request.destroy(Error('Registry response too large')); });
      response.on('end', () => { try { resolve(JSON.parse(body).version); } catch (error) { reject(error); } });
      response.on('error', reject);
    });
    request.setTimeout(2000, () => request.destroy(Error('Registry timeout')));
    request.on('error', reject);
  });
}

async function checkForUpdate({ interactive, current, args, latest, ask, launch }) {
  if (!interactive) return null;
  let version;
  try { version = await latest(); } catch { return null; }
  if (typeof version !== 'string' || !newer(version, current)) return null;
  if (!await ask(version)) return null;
  return launch(version, args);
}

function ask(version) {
  return new Promise(resolve => {
    const terminal = readline.createInterface({ input: process.stdin, output: process.stderr });
    terminal.question(`Panda Suite ${version} is available. Run this command with the newer version? [y/N] `, answer => {
      resolve(/^y(?:es)?$/i.test(answer.trim())); terminal.close();
    });
    terminal.on('close', () => resolve(false));
  });
}

function launch(version, args) {
  const command = process.platform === 'win32' ? 'npx.cmd' : 'npx';
  const result = spawnSync(command, ['--yes', `panda-suite@${version}`, ...args], { stdio: 'inherit', env: { ...process.env, PANDA_SUITE_SKIP_UPDATE_CHECK: '1' } });
  if (result.error) {
    // The newer version never started (for example, Node on Windows refuses to
    // spawn npx.cmd without a shell). Fall back so the requested command still runs.
    console.error(`panda-suite: could not run ${version} (${result.error.message}); continuing with the current version`);
    return null;
  }
  return result.status === null ? 1 : result.status;
}

module.exports = { checkForUpdate, latestVersion, ask, launch };
