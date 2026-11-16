'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const version = require('../package.json').version;
const sourceRoot = path.join(__dirname, '..', 'skills');
// npm omits .gitignore files from packages; restore their original bytes in staging.
const packagedFiles = require('./packaged-files.json');
const stateName = '.panda-suite-state.json';
const lockName = '.panda-suite-lock';
const journalName = '.panda-suite-transaction';
const validName = name => /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name);
const exists = p => { try { fs.lstatSync(p); return true; } catch (e) { if (e.code === 'ENOENT') return false; throw e; } };
function directory(p) {
  const stat = fs.lstatSync(p);
  if (!stat.isDirectory() || stat.isSymbolicLink()) throw Error(`Unsafe directory: ${p}`);
}
function tree(root) {
  directory(root);
  const files = Object.create(null);
  function walk(dir, prefix) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      const full = path.join(dir, entry.name);
      const stat = fs.lstatSync(full);
      if (stat.isSymbolicLink()) throw Error(`Symlink refused: ${full}`);
      if (stat.isDirectory()) walk(full, rel);
      else if (stat.isFile()) files[rel] = crypto.createHash('sha256').update(fs.readFileSync(full)).digest('hex');
      else throw Error(`Unsupported file: ${full}`);
    }
  }
  walk(root, '');
  return files;
}
function equal(a, b) {
  const keys = Object.keys(a).sort();
  return keys.length === Object.keys(b).length && keys.every(key => a[key] === b[key]);
}
function readState(dest, required) {
  const file = path.join(dest, stateName);
  if (!exists(file)) { if (required) throw Error(`No managed state at ${file}; install skills first`); return { schemaVersion: 1, packageVersion: version, skills: {} }; }
  if (!fs.lstatSync(file).isFile() || fs.lstatSync(file).isSymbolicLink()) throw Error(`Unsafe state file: ${file}`);
  let data;
  try { data = JSON.parse(fs.readFileSync(file, 'utf8')); } catch { throw Error(`Invalid state: ${file}`); }
  if (!data || data.schemaVersion !== 1 || typeof data.packageVersion !== 'string' || !/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(data.packageVersion) || !data.skills || typeof data.skills !== 'object' || Array.isArray(data.skills)) throw Error(`Invalid or unsupported state: ${file}`);
  for (const [name, record] of Object.entries(data.skills)) {
    if (!validName(name) || !record || !record.files || typeof record.files !== 'object' || Array.isArray(record.files)) throw Error(`Invalid state entry: ${name}`);
    for (const [rel, hash] of Object.entries(record.files)) {
      if (!rel || rel.includes('\\') || rel.split('/').some(part => !part || part === '.' || part === '..') || !/^[a-f0-9]{64}$/.test(hash)) throw Error(`Invalid state path or hash: ${rel}`);
    }
  }
  return data;
}
function verifyInstalled(dest, state) {
  for (const [name, record] of Object.entries(state.skills)) {
    const target = path.join(dest, name);
    if (!exists(target) || !equal(tree(target), record.files)) throw Error(`Managed skill changed or missing: ${target}. Restore it from backup before retrying.`);
  }
}
function run(options) {
  const dest = options.destination;
  if (options.command === 'update' && !exists(dest)) throw Error(`No managed state at ${path.join(dest, stateName)}; install skills first`);
  fs.mkdirSync(dest, { recursive: true });
  directory(dest);
  const lock = path.join(dest, lockName), journal = path.join(dest, journalName);
  if (exists(journal)) throw Error(`Interrupted transaction at ${journal}; follow README recovery instructions before retrying.`);
  try { fs.mkdirSync(lock); } catch (e) { if (e.code === 'EEXIST') throw Error(`Destination locked: ${lock}; if no process is running, follow README recovery instructions.`); throw e; }
  try {
    if (exists(journal)) throw Error(`Interrupted transaction at ${journal}; follow README recovery instructions.`);
    const state = readState(dest, options.command === 'update');
    verifyInstalled(dest, state);
    const available = fs.readdirSync(sourceRoot).filter(name => validName(name) && fs.existsSync(path.join(sourceRoot, name, 'SKILL.md'))).sort();
    let names = options.command === 'install' ? (options.all ? available : [...new Set(options.names)]) : Object.keys(state.skills).sort();
    for (const name of names) if (!validName(name)) throw Error(`Invalid skill name: ${name}`);
    const skipped = [];
    if (options.command === 'update') names = names.filter(name => { if (!available.includes(name)) { skipped.push(name); return false; } return true; });
    for (const name of names) {
      if (!available.includes(name)) throw Error(`Unknown skill: ${name}`);
      tree(path.join(sourceRoot, name));
      if (options.command === 'install' && exists(path.join(dest, name))) throw Error(`Skill already exists: ${path.join(dest, name)}. Back it up before installing.`);
    }
    fs.mkdirSync(journal);
    const staged = path.join(journal, 'staged'), backup = path.join(journal, 'backup');
    fs.mkdirSync(staged); fs.mkdirSync(backup);
    const oldState = path.join(dest, stateName);
    if (exists(oldState)) fs.copyFileSync(oldState, path.join(journal, 'state.before'), fs.constants.COPYFILE_EXCL);
    const manifest = { command: options.command, names, hadState: exists(oldState) };
    fs.writeFileSync(path.join(journal, 'manifest.json'), JSON.stringify(manifest, null, 2), { flag: 'wx' });
    const movedOld = [], movedNew = [];
    let committed = false;
    try {
      for (const name of names) {
        fs.cpSync(path.join(sourceRoot, name), path.join(staged, name), { recursive: true, errorOnExist: true, force: false });
        for (const [rel, content] of Object.entries(packagedFiles)) {
          const prefix = `skills/${name}/`;
          if (!rel.startsWith(prefix)) continue;
          const parts = rel.slice(prefix.length).split('/');
          if (parts.some(part => !part || part === '.' || part === '..' || part.includes('\\'))) throw Error(`Invalid packaged path: ${rel}`);
          const output = path.join(staged, name, ...parts);
          if (!exists(output)) { fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, Buffer.from(content, 'base64'), { flag: 'wx' }); }
          else if (!fs.readFileSync(output).equals(Buffer.from(content, 'base64'))) throw Error(`Packaged file differs from source: ${rel}`);
        }
        state.skills[name] = { files: tree(path.join(staged, name)) };
      }
      // Compare against the original on-disk state, not the newly computed hashes.
      verifyInstalled(dest, readState(dest, options.command === 'update'));
      for (const name of names) {
        const target = path.join(dest, name);
        if (options.command === 'install' && exists(target)) throw Error(`Late collision: ${target}`);
        if (options.command === 'update') {
          fs.renameSync(target, path.join(backup, name)); movedOld.push(name);
          fs.renameSync(path.join(staged, name), target); movedNew.push(name);
        } else {
          // Reserve exclusively so a late collision cannot be replaced by rename.
          fs.mkdirSync(target); movedNew.push(name);
          fs.cpSync(path.join(staged, name), target, { recursive: true, errorOnExist: true, force: false });
        }
      }
      state.packageVersion = version;
      const newState = path.join(journal, 'state.after');
      fs.writeFileSync(newState, `${JSON.stringify(state, null, 2)}\n`, { flag: 'wx' });
      fs.renameSync(newState, oldState); committed = true;
    } catch (e) {
      try {
        for (const name of movedNew.reverse()) fs.rmSync(path.join(dest, name), { recursive: true });
        for (const name of movedOld.reverse()) fs.renameSync(path.join(backup, name), path.join(dest, name));
        fs.rmSync(journal, { recursive: true });
      } catch (rollback) { throw Error(`${e.message}; rollback failed: ${rollback.message}. Preserve ${journal} and follow recovery instructions.`); }
      throw e;
    }
    if (committed) fs.rmSync(journal, { recursive: true });
    for (const name of names) console.log(`${options.command === 'install' ? 'Installed' : 'Updated'} ${name}`);
    for (const name of skipped) console.log(`Skipped ${name}: absent from package; retained`);
    console.log(`Panda Suite ${version}`);
  } finally { fs.rmSync(lock, { recursive: true, force: true }); }
}
module.exports = { run };
